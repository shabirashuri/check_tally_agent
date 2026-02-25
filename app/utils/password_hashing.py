from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pass(password: str):
    # truncate password to 72 bytes to avoid bcrypt errors
    return pwd_context.hash(password[:72])

def verify_pass(password: str, hashed: str):
    return pwd_context.verify(password, hashed)