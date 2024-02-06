from decouple import config
from datetime import datetime, timedelta
from jose import JWTError, jwt

from models import User
from db import get_user_by_username

# Access environment variables
DATABASE_URL = config("DATABASE_URL")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
SECRET_KEY = config("SECRET_KEY")
debug_mode = config("DEBUG", default=False, cast=bool)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(username: str, password: str) -> User:
    user = await get_user_by_username(username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user
