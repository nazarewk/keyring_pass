import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='keyring_password_store',
        version='0.1.0',
        packages=['keyring_password_store'],
        entry_points={
            'keyring.backends': [
                'pass = keyring_password_store'
            ]
        }
    )
