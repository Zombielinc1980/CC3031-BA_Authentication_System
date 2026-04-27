import uuid
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password, salt):
    return generate_password_hash(password + salt, method="pbkdf2:sha256")

def check_password(password_hash, password, salt):
    return check_password_hash(password_hash, password + salt)

def generate_salt():
    return uuid.uuid4().hex