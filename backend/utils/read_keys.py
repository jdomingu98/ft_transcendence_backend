import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def read_private_key():
    private_key_path = os.getenv('JWT_PRIVATE_KEY_PATH')
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

def read_public_key():
    public_key_path = os.getenv('JWT_PUBLIC_KEY_PATH')
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return public_key
