# keyring_pass

This is a [`pass`](https://www.passwordstore.org/) backend for [`keyring`](https://pypi.org/project/keyring/)

Install with `pip install keyring-pass` and set the following content in your `keyringrc.cfg` file:

```
[backend]
default-keyring=keyring_pass.PasswordStoreBackend
```
