from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import models
import schemas
from database import SessionLocal
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )

        return {
            "username": username,
            "id": user_id
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

@router.post("/register", response_model=schemas.UserResponse)
def register_user(
    user: schemas.UserRegister,
    db: Session = db_dependency
):
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = pwd_context.hash(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


@router.post("/login", response_model=schemas.Token)
def login_user(
    user: OAuth2PasswordRequestForm = Depends(),
    db: Session = db_dependency
):
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token({
        "sub": existing_user.username,
        "id": existing_user.id
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get("/test")
def test_user(
    user: dict = Depends(get_current_user)
):
    return {
        "message": "You are authenticated",
        "user": user
    }