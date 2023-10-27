import os
import random
import string
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from starlette.status import HTTP_302_FOUND

from api_models.redis_connector import AppRedisConnector
from create_app import config, app
from exceptions import JWTIsFailException
from services.tg_bot import send_message

router = APIRouter()
templates = Jinja2Templates(directory=f"{os.getcwd()}/templates")

admins = config.tg_bot.admins


class SUserAuth(BaseModel):
    login: str
    password: str


def verify_user(user: SUserAuth) -> bool:
    return config.auth.login == user.login and config.auth.password == user.password


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=5)
    to_encode.update({"exp": expire})
    return jwt.encode(claims=to_encode, key=config.auth.secret_key, algorithm=config.auth.algorithm)


async def authenticate_user(user: SUserAuth):
    if verify_user(user=user):
        return True
    return False


def get_token(request: Request):
    token = request.cookies.get("estate_app_access_token")
    if not token:
        raise JWTIsFailException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token=token, key=config.auth.secret_key, algorithms=config.auth.algorithm)
    except JWTError:
        raise JWTIsFailException
    login: str = payload.get("sub")
    if not login:
        raise JWTIsFailException
    if login != config.auth.login:
        raise JWTIsFailException
    return login


async def create_and_send_telegram_auth():
    letters = string.ascii_lowercase
    code = ''.join(random.choice(letters) for i in range(12))
    text = f"Код для входа в приложение:\n<code>{code}</code>\nДля удобства можно кликнуть по коду, он будет " \
           "скопирован.\nКод действует 5 минут"
    for admin in admins:
        await send_message(receiver=admin, text=text)
    AppRedisConnector.set_tlg_code(code=code)


@router.get("/login", response_class=HTMLResponse)
async def auth_page(request: Request, is_start: bool = True, is_login: bool = True):
    return templates.TemplateResponse("auth.html", {"request": request, "is_start": is_start, "is_login": is_login})


@router.post("/check_login", response_class=HTMLResponse)
async def auth_page(request: Request, login: str = Form(), password: str = Form()):
    is_verified = await authenticate_user(user=SUserAuth(login=login, password=password))
    if is_verified:
        await create_and_send_telegram_auth()
        return templates.TemplateResponse("auth.html", {"request": request, "is_start": True, "is_login": False})
    else:
        response = RedirectResponse(url="/incorrect_auth", status_code=HTTP_302_FOUND)
    return response


@router.post("/check_code", response_class=HTMLResponse)
async def code_page(request: Request, tlg_form_code: str = Form()):
    tlg_redis_code = AppRedisConnector.get_tlg_code()
    if tlg_redis_code["code"] == tlg_form_code:
        access_token = create_access_token({"sub": str(config.auth.login)})
        response = RedirectResponse(url="/", status_code=HTTP_302_FOUND)
        response.set_cookie("estate_app_access_token", access_token, httponly=True)
    else:
        response = RedirectResponse(url="/incorrect_auth", status_code=HTTP_302_FOUND)
    return response


@router.get("/incorrect_auth", response_class=HTMLResponse)
async def incorrect_auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "is_start": False, "is_login": True})


@app.exception_handler(JWTIsFailException)
async def not_correct_auth_data(request: Request, exc: JWTIsFailException):
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
