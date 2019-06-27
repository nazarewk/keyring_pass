import shutil
import sys

import setuptools

if __name__ == '__main__':
    executable = shutil.which('pass')
    if not executable:
        sys.exit('`pass` executable not found util not found in your PATH!')
    print('`pass` found at {}'.format(executable))

    setuptools.setup(
        name='keyring_password_store',
        python_requires='>3.3',
        version='0.1.0',
        packages=['keyring_password_store'],
        entry_points={
            'keyring.backends': [
                'pass = keyring_password_store'
            ]
        },
        install_requires=[
            'keyring'
        ]
    )
