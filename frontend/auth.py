import hashlib
from typing import Optional, Dict

# In-memory user store (replace with real IdP / OAuth in production)
# Passwords are SHA256-hashed for demo purposes only.
_USERS: Dict[str, Dict] = {
    "doctor@example.com": {
        "password_hash": hashlib.sha256("Doctor@123".encode()).hexdigest(),
        "role": "doctor"
    },
    "patient@example.com": {
        "password_hash": hashlib.sha256("Patient@123".encode()).hexdigest(),
        "role": "patient"
    },
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(email: str, password: str) -> bool:
    user = _USERS.get(email)
    if not user:
        return False
    return user["password_hash"] == hash_password(password)


def get_user_by_email(email: str) -> Optional[Dict]:
    return _USERS.get(email)
