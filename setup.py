import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='keyring_pass',
        python_requires='>3.3',
        version='0.2.0',
        packages=['keyring_pass'],
        entry_points={
            'keyring.backends': [
                'pass = keyring_pass'
            ]
        },
        install_requires=[
            'keyring'
        ]
    )
