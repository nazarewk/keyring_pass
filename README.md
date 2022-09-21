# keyring_pass

This is a [`pass`](https://www.passwordstore.org/) backend for [`keyring`](https://pypi.org/project/keyring/)

Install with `pip install keyring-pass` and set the following content in your [`keyringrc.cfg`](https://pypi.org/project/keyring/#config-file-path) file:

```ini
[backend]
default-keyring=keyring_pass.PasswordStoreBackend
```

You can modify the default `python-keyring` prefix for `pass`, by:
- adding following to `keyringrc.cfg`:
  
    ```ini
    [pass]
    key-prefix=alternative/prefix/path
    ```

- (for `keyring` version 23.0.0 or higher) setting environment variable `KEYRING_PROPERTY_PASS_KEY_PREFIX`

- You can clear the path (start from root), by setting above to `.` or an empty value (just `key-prefix=` on the line).


## Test your setup

You can check if your setup works end-to-end (creates, reads and deletes a key from password store).

```shell
# warning: this will create and delete a key at `<prefix>/test/asd` in your password store
python -m keyring_pass
```
