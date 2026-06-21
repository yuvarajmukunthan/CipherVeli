import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(password.encode())

def encrypt(data: bytes, password: str) -> bytes:
    """Encrypts data using AES-256-GCM with a password."""
    if not password:
        return data
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return salt + nonce + ciphertext

def decrypt(data: bytes, password: str) -> bytes:
    """Decrypts data using AES-256-GCM with a password."""
    if not password:
        return data
    if len(data) < 28:
        raise ValueError("Data is too short to contain encryption metadata.")
    salt = data[:16]
    nonce = data[16:28]
    ciphertext = data[28:]
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)
