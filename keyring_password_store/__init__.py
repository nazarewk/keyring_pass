import codecs
import subprocess
import sys

import keyring
from keyring import backend


def command(cmd, **kwargs):
    kwargs.setdefault('stderr', sys.stderr)
    try:
        output = subprocess.check_output(cmd, **kwargs)
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stdout.decode('utf8'))
        raise
    return codecs.decode(output, 'utf8')


class PasswordStoreBackend(backend.KeyringBackend):
    priority = 1

    def get_key(self, servicename, username):
        return '/'.join(('python-keyring', servicename, username))

    def set_password(self, servicename, username, password):
        if isinstance(password, str):
            password = password.encode('utf8')

        inp = password + b'\n'
        inp *= 2

        command(['pass', 'insert', '-f', self.get_key(servicename, username)], input=inp)

    def get_password(self, servicename, username):
        try:
            return command(['pass', self.get_key(servicename, username)])[:-1]
        except subprocess.CalledProcessError as exc:
            pattern = b'not in the password store'
            if pattern in exc.output:
                return None
            raise

    def delete_password(self, service, username):
        command(['pass', 'rm', self.get_key(service, username)])


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
