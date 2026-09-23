"""Session and password helpers."""
import base64
import hashlib
import os
import pickle


def load_session(cookie_value):
    return pickle.loads(base64.b64decode(cookie_value))


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_safe(password):
    salt = os.urandom(16)
    return salt + hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
