import base64
import codecs
import os
import shutil
import subprocess
import sys

import keyring
from keyring import backend
from keyring.util import properties


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


def b64encode(value):
    if isinstance(value, str):
        value = value.encode('utf8')

    encoded = base64.b64encode(value)

    return encoded.decode('utf8')


class PasswordStoreBackend(backend.KeyringBackend):
    @properties.ClassProperty
    @classmethod
    def priority(cls):
        if not shutil.which('pass'):
            raise RuntimeError('`pass` executable is missing!')

        command(['pass', 'ls'])
        return 1

    def get_key(self, service, username):
        return os.path.sep.join((
            'python-keyring',
            b64encode(service),
            b64encode(username),
        ))

    def set_password(self, servicename, username, password):
        """

        :type password: str
        """
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
