import os
from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from sqlmodel import Session, select
from starlette import status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from exceptions import NotAuthenticatedException
from db import get_session
from schemas import UserOutput, User
from dotenv import load_dotenv
from fastapi_login.exceptions import InvalidCredentialsException  # Exception class

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
URL_PREFIX = "/auth"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{URL_PREFIX}/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
manager = LoginManager(SECRET_KEY, token_url=f'{URL_PREFIX}/login')
router = APIRouter(prefix=URL_PREFIX)


@manager.user_loader()
def load_user(username: str, session: Session):  # could also be an asynchronous function
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    return user


# This will be deprecated in the future
# set your exception when initiating the instance
# manager = LoginManager(..., custom_exception=NotAuthenticatedException)
manager.not_authenticated_exception = NotAuthenticatedException

templates = Jinja2Templates(directory="templates")


# these two argument are mandatory
def exc_handler(request, exc):
    return RedirectResponse(url='/auth/login')

# used in api
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> UserOutput:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    user = load_user(username, session)
    if user:
        return UserOutput.from_orm(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.get("/login")
def loginwithCreds(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )


@router.post("/login")
def web_login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = load_user(form_data.username, session)
    if user and user.verify_password(form_data.password):
        access_token = create_access_token(data={"sub": user.username})  # type: ignore
        resp = RedirectResponse(url="/private", status_code=status.HTTP_302_FOUND)
        manager.set_cookie(resp, access_token)
        return resp
    else:
        raise InvalidCredentialsException


@router.post("/token")
def api_login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = load_user(form_data.username, session)
    if user and user.verify_password(form_data.password):
        access_token = create_access_token(data={"sub": user.username})  # type: ignore
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise InvalidCredentialsException
