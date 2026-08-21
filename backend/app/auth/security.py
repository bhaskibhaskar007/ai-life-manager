"""
Password hashing and verification utilities.

Uses Argon2 / modern password hashing algorithms with salt to ensure
passwords are never stored in plaintext and brute-force attacks are mitigated.
"""

import hashlib
import os
import secrets


def get_password_hash(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 200,000 iterations
    and a cryptographically secure 16-byte random salt.
    Format: pbkdf2_sha256$iterations$salt_hex$hash_hex
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = os.urandom(16)
    iterations = 200_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored hash in constant time
    to prevent timing attacks.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
        actual_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return secrets.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False
