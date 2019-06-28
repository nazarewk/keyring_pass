import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='keyring_pass',
    version='0.3.0',
    author='Krzysztof Nazarewski',
    author_email='3494992+nazarewk@users.noreply.github.com',
    description='https://www.passwordstore.org/ backend for https://pypi.org/project/keyring/',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/nazarewk/keyring_pass',

    python_requires='>3.3',
    packages=['keyring_pass'],

    entry_points={
        'keyring.backends': [
            'pass = keyring_pass'
        ]
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        'keyring'
    ]
)
