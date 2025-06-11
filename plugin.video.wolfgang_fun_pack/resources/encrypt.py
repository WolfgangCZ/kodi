from passlib.hash import md5_crypt
import hashlib

def encrypt_password(password: str, salt: str):
    """Encrypt password according to API requirements"""
    md5_crypt_password = md5_crypt.using(salt=salt).hash(password)
    sha1_password = hashlib.sha1(md5_crypt_password.encode("ascii")).hexdigest().lower()
    return sha1_password