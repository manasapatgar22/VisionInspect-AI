from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


SECRET_KEY = "visioninspect-development-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


class RegisterRequest(BaseModel):

    username: str
    email: str
    password: str
    role: str = "quality_engineer"


class LoginRequest(BaseModel):

    username: str
    password: str


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    username: str
) -> str:

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    allowed_roles = {
        "quality_engineer",
        "factory_supervisor"
    }

    if request.role not in allowed_roles:

        raise HTTPException(
            status_code=400,
            detail="Invalid role."
        )

    existing_user = (
        db.query(User)
        .filter(User.username == request.username)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    existing_email = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )

    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(
            request.password
        ),
        role=request.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.username == request.username)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    token = create_access_token(
        user.username
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user