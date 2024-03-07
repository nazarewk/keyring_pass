import sys

import keyring

from keyring_pass import PasswordStoreBackend
svc = "test"
user = "asd"
pwd = "zxc"

keyring.set_keyring(PasswordStoreBackend())
errors = []
print(f"testing with {svc=} {user=} {pwd=}")

try:
    keyring.set_password(svc, user, pwd)
    returned = keyring.get_password(svc, user)
    credential = keyring.get_credential(svc, None)
finally:
    keyring.delete_password(svc, user)

if returned != pwd:
    errors.append(f"get_password(): {returned=} != {pwd=}")
else:
    print(f"OK: get_password(): matches")

if not credential:
    errors.append(f"get_credential() not found ({credential=})")
else:
    print(f"OK: get_credential(): found")
    if credential.username != user:
        errors.append(
            f"get_credential(): {credential.username=} doesn't match {user=}"
        )
    else:
        print(f"OK: get_credential(): username matches")

    if credential.password != pwd:
        errors.append(
            f"get_credential(): {credential.password=} doesn't match {pwd=}"
        )
    else:
        print(f"OK: get_credential(): password matches")

for err in errors:
    print(f"ERROR: {err}")
if errors:
    sys.exit(1)
