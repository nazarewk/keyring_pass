import codecs
import configparser
import functools
import os
import shutil
import subprocess
import sys

import keyring
from jaraco.classes import properties
from keyring import backend
from keyring.util import platform_ as platform

try:
    from functools import cache
except ImportError:
    from functools import lru_cache
    cache = lru_cache(maxsize=None)


def command(cmd, **kwargs):
    kwargs.setdefault("stderr", sys.stderr)
    try:
        output = subprocess.check_output(cmd, **kwargs)
    except subprocess.CalledProcessError as exc:
        pattern = b"password store is empty"
        if pattern in exc.output:
            raise RuntimeError(exc.output)
        sys.stderr.write(exc.stdout.decode("utf8"))
        raise
    return codecs.decode(output, "utf8")


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

    INI_OPTIONS = {
        "pass_key_prefix": "key-prefix",
        "pass_binary": "binary",
    }

    def __init__(self):
        for k, v in _load_config().items():
            setattr(self, k, v)
        super().__init__()

    @properties.classproperty
    def priority(cls):
        binary = _load_config().get("pass_binary", cls.pass_binary)
        if not shutil.which(binary):
            raise RuntimeError(f"`{binary}` executable is missing!")

        command([binary, "ls"])
        return 1

    def get_key(self, service, username):
        return os.path.join(
            self.pass_key_prefix,
            service,
            username,
        )

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
            input=inp.encode("utf8"),
        )

    def get_password(self, servicename, username):
        try:
            ret = command(["pass", "show", self.get_key(servicename, username)])
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 1:
                return None
            raise
        return ret.splitlines()[0]

    def delete_password(self, service, username):
        command([self.pass_binary, "rm", "--force", self.get_key(service, username)])


if __name__ == "__main__":
    svc = "test"
    user = "asd"
    pwd = "zxc"

    keyring.set_keyring(PasswordStoreBackend())

    try:
        keyring.set_password(svc, user, pwd)
        returned = keyring.get_password(svc, user)

    finally:
        keyring.delete_password(svc, user)

    if returned != pwd:
        print("{} != {}".format(returned, pwd))
        sys.exit(1)
