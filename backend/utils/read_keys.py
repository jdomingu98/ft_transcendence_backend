import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def read_private_key():
    private_key_path = os.getenv("JWT_PRIVATE_KEY_PATH")
    private_key_password = os.getenv("JWT_PRIVATE_KEY_PASSWORD")
    if private_key_password:
        private_key_password = private_key_password.encode()
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=private_key_password, backend=default_backend()
        )
    return private_key


def read_public_key():
    public_key_path = os.getenv("JWT_PUBLIC_KEY_PATH")
    with open(public_key_path, "rb") as key_file:
        public_key = key_file.read()

    return public_key
