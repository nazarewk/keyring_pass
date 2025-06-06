# -*- coding: utf-8 -*-
import configparser
import os
import re
import shutil
import subprocess
import sys
import pathlib

import keyring
from jaraco.classes import properties
from keyring import backend, credentials
from keyring.util import platform_ as platform

try:
    from functools import cache
except ImportError:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


def command(cmd, **kwargs) -> str:
    kwargs.setdefault("encoding", "utf8")
    kwargs.setdefault("stderr", sys.stderr)
    try:
        return subprocess.check_output(cmd, **kwargs)
    except subprocess.CalledProcessError as exc:
        pattern = "password store is empty"
        if pattern in exc.output:
            raise RuntimeError(exc.output)
        sys.stderr.write(exc.stdout)
        raise


@cache
def _load_config(
    keyring_cfg=os.path.join(platform.config_root(), "keyringrc.cfg"),
):
    cfg = {}
    if not os.path.exists(keyring_cfg):
        return cfg

    config = configparser.RawConfigParser()
    config.read(keyring_cfg)
    for attr, option in PasswordStoreBackend.INI_OPTIONS.items():
        try:
            cfg[attr] = config.get("pass", option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
    return cfg


class PasswordStoreBackend(backend.KeyringBackend):
    pass_key_prefix = "python-keyring"
    pass_binary = "pass"
    pass_exact_service = True
    pass_directory = os.getenv('PASSWORD_STORE_DIR',
                               os.path.join(
                                   os.getenv('HOME'), '/.password-store'))

    INI_OPTIONS = {
        "pass_key_prefix": "key-prefix",
        "pass_binary": "binary",
        "pass_exact_service": "exact-service",
    }

    def __init__(self):
        for k, v in _load_config().items():
            setattr(self, k, v)
        if isinstance(self.pass_exact_service, str):
            self.pass_exact_service = self.pass_exact_service.lower() == "true"
        self.pass_key_prefix = os.path.normpath(self.pass_key_prefix)
        super().__init__()

    def _password_key(self, password, *args):
        try:
            ret = command(
                [self.pass_binary, "show", password]
            )
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 1:
                return None
            raise
        for line in ret.splitlines():
            k = line.split(':')
            for arg in args:
                if k[0] == arg:
                    return k[1]
        return False

    def _password_login(self, password):
        return self._password_key(password, 'login', 'user')


    @properties.classproperty
    def priority(cls):
        binary = _load_config().get("pass_binary", cls.pass_binary)
        if not shutil.which(binary):
            raise RuntimeError(f"`{binary}` executable is missing!")

        command([binary, "ls"])
        return 1

    def get_key(self, service, username):
        keyring_path = pathlib.Path(
            os.path.join(self.pass_directory,
                         self.pass_key_prefix))
        if username:
            key_glob = keyring_path.rglob(
                os.path.join(service, username + '.gpg'))
            for key in key_glob:
                return key.relative_to(self.pass_directory).with_suffix('')
        key_glob = keyring_path.rglob(service + '.gpg')

        for key in key_glob:
            key = key.relative_to(self.pass_directory).with_suffix('')
            if username:
                p_user = self._password_login(key)
                if p_user == username: return key
            return key
        # Fallback
        return os.path.join(self.pass_key_prefix, service, username)

    def set_password(self, servicename, username, password):
        password = password.splitlines()[0]
        inp = "%s\n" % password
        inp *= 2

        command(
            [
                self.pass_binary,
                "insert",
                "--force",
                self.get_key(servicename, username),
            ],
            input=inp,
        )

    def get_credential(self, servicename, username):
        if username:
            return credentials.SimpleCredential(
                username,
                self.get_password(servicename, username),
            )
        try:
            servicename = os.path.normpath(servicename)
            service_key = self.get_key(servicename, None)
            output = command([self.pass_binary, "ls", service_key])
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 1:
                return None
            raise
        # Currently pass only has tree like structure output.
        # Internally it uses the command tree but does not pass
        # output formatter options (e.g., for json).
        lines = output.splitlines()
        lines = [re.sub(r"\x1B\[([0-9]+;)?[0-9]+m", "", line) for line in lines]

        # Assumption that output paths must contain leaves.
        # Services and users are entries in our keyring. Thus remove any
        # non-word char from the left.
        entries = [re.sub(r"^\W+", "", line) for line in lines]
        # Just in case: Remove empty entries and corresponding lines
        indents, entries = zip(
            *[
                (len(line) - len(entry), entry)
                for line, entry in zip(lines, entries)
                if entry
            ]
        )
        # The count of removed characters tells us how far elements are indented.
        # Elements with the same count are on the same level.
        # EOF tree is at indent 0 again.
        indents = list(indents) + [0]
        entries = list(entries)
        # Now to identify the user entries from service keys we must identify
        # which elements do not have further entries further down the structure.
        # This means that the next element is not indented any further.
        users_ids = [
            i for i, j in enumerate(zip(indents[:-1], indents[1:])) if j[0] >= j[1]
        ]
        # A user with the least indent is closest to the specified service path.
        users_ids = sorted(users_ids, key=lambda i: indents[i])

        # Parse hierarchy and get complete path
        if users_ids:
            idx = users_ids[0]
            username = entries[idx]
            # current level of the last added service key
            branch_indent = indents[idx]
            # last level that can be added
            # so stop there.
            top_indent = indents[1]
            paths = []

            while branch_indent > top_indent:
                idx = idx - 1
                # higher up in the tree or same level
                indent = indents[idx]
                if indent < branch_indent:
                    # less indented means new service key
                    paths.insert(0, entries[idx])
                    branch_indent = indent

            found_service = os.path.join(servicename, *paths) if paths else servicename

            if (not self.pass_exact_service) or servicename == found_service:
                return credentials.SimpleCredential(
                    username, self.get_password(found_service, username)
                )
        return None

    def get_password(self, servicename, username):
        try:
            ret = command(
                [self.pass_binary, "show", self.get_key(servicename, username)]
            )
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 1:
                return None
            raise
        return ret.splitlines()[0]

    def delete_password(self, service, username):
        command([self.pass_binary, "rm", "--force", self.get_key(service, username)])


