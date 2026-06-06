import hashlib
import secrets
from datetime import datetime, timedelta

ADMIN_PASSWORD_HASH = hashlib.sha256('admin123'.encode()).hexdigest()
VALID_TOKENS = {}
TOKEN_EXPIRY = 24

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth(password):
    password_hash = hash_password(password)
    return password_hash == ADMIN_PASSWORD_HASH

def generate_session_token():
    token = secrets.token_urlsafe(32)
    VALID_TOKENS[token] = datetime.now() + timedelta(hours=TOKEN_EXPIRY)
    return token

def check_token(token):
    if token not in VALID_TOKENS:
        return False
    if VALID_TOKENS[token] < datetime.now():
        del VALID_TOKENS[token]
        return False
    return True

def cleanup_expired_tokens():
    expired = [t for t, exp in VALID_TOKENS.items() if exp < datetime.now()]
    for token in expired:
        del VALID_TOKENS[token]
