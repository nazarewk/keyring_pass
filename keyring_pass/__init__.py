import codecs
import configparser
import os
import shutil
import subprocess
import sys

import keyring
from jaraco.classes import properties
from keyring import backend
from keyring.util import platform_ as platform


def command(cmd, **kwargs):
    kwargs.setdefault('stderr', sys.stderr)
    try:
        output = subprocess.check_output(cmd, **kwargs)
    except subprocess.CalledProcessError as exc:
        pattern = b'password store is empty'
        if pattern in exc.output:
            raise RuntimeError(exc.output)
        sys.stderr.write(exc.stdout.decode('utf8'))
        raise
    return codecs.decode(output, 'utf8')


class PasswordStoreBackend(backend.KeyringBackend):
    pass_key_prefix = 'python-keyring'

    def __init__(self):
        super().__init__()
        self._load_config()

    def _load_config(self):
        keyring_cfg = os.path.join(platform.config_root(), 'keyringrc.cfg')
        if not os.path.exists(keyring_cfg):
            return

        config = configparser.RawConfigParser()
        config.read(keyring_cfg)
        try:
            self.pass_key_prefix = config.get('pass', 'key-prefix')
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

    @properties.classproperty
    @classmethod
    def priority(cls):
        if not shutil.which('pass'):
            raise RuntimeError('`pass` executable is missing!')

        command(['pass', 'ls'])
        return 1

    def get_key(self, service, username):
        return os.path.join(
            self.pass_key_prefix,
            service,
            username,
        )

    def set_password(self, servicename, username, password):
        password = password.splitlines()[0]
        inp = '%s\n' % password
        inp *= 2

        command(['pass', 'insert', '--force', self.get_key(servicename, username)], input=inp.encode('utf8'))

    def get_password(self, servicename, username):
        try:
            ret = command(['pass', 'show', self.get_key(servicename, username)])
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 1:
                return None
            raise
        return ret.splitlines()[0]

    def delete_password(self, service, username):
        command(['pass', 'rm', '--force', self.get_key(service, username)])


if __name__ == '__main__':
    svc = 'test'
    user = 'asd'
    pwd = 'zxc'

    try:
        keyring.set_password(svc, user, pwd)
        returned = keyring.get_password(svc, user)

    finally:
        keyring.delete_password(svc, user)

    if returned != pwd:
        print('{} != {}'.format(returned, pwd))
        sys.exit(1)
