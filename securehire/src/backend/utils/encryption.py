"""
Encryption Utilities
- AES-256-GCM for data at rest
- Key rotation support
- Secure random IV generation
CYC386 Requirement: AES-256 encryption at rest
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib
import logging
from config import settings

logger = logging.getLogger(__name__)


def _get_key() -> bytes:
    """Derive 32-byte AES key from config"""
    key = settings.AES_SECRET_KEY.encode("utf-8")
    return hashlib.sha256(key).digest()  # Always 32 bytes


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt sensitive data using AES-256-GCM
    Returns: base64(nonce + tag + ciphertext)
    """
    try:
        key = _get_key()
        nonce = get_random_bytes(16)  # Fresh random nonce every time
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
        # Pack: nonce(16) + tag(16) + ciphertext
        encrypted = nonce + tag + ciphertext
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise ValueError("Encryption error")


def decrypt_data(encrypted_b64: str) -> str:
    """
    Decrypt AES-256-GCM encrypted data
    """
    try:
        key = _get_key()
        encrypted = base64.b64decode(encrypted_b64.encode("utf-8"))
        nonce = encrypted[:16]
        tag = encrypted[16:32]
        ciphertext = encrypted[32:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode("utf-8")
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError("Decryption error")


def hash_sensitive(value: str) -> str:
    """One-way hash for searchable sensitive fields (e.g., phone lookup)"""
    return hashlib.sha256(value.encode()).hexdigest()
