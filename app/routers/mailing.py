from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse

from api_models.sql_connector import UsersDAO
from create_app import templates
from routers.auth import SUserAuth, get_current_user
from services.tg_bot import send_message

router = APIRouter()


@router.get("/mailing", response_class=HTMLResponse)
async def mailing_page(request: Request, user: SUserAuth = Depends(get_current_user)):
    return templates.TemplateResponse("mailing.html", {"request": request, "success_data": None})


@router.post("/sent_mailing", response_class=HTMLResponse)
async def get_mail_page(request: Request,
                        brochures_low: int = Form(default=0),
                        brochures_high: int = Form(default=10 ** 6),
                        calc_low: int = Form(default=0),
                        calc_high: int = Form(default=10 ** 6),
                        telegraph_low: int = Form(default=0),
                        telegraph_high: int = Form(default=10 ** 6),
                        text: str = Form(default=""),
                        user: SUserAuth = Depends(get_current_user)):
    users = await UsersDAO.get_users_for_mailing(data=dict(brochures_low=brochures_low,
                                                           brochures_high=brochures_high,
                                                           calc_low=calc_low,
                                                           calc_high=calc_high,
                                                           telegraph_low=telegraph_low,
                                                           telegraph_high=telegraph_high))
    success_counter = 0
    for user in users[:1]:
        resp_status = await send_message(receiver=user["user_id"], text=text)
        if resp_status == 200:
            success_counter += 1
    success_data = dict(success_counter=success_counter, total_length=len(users))
    return templates.TemplateResponse("mailing.html", {"request": request, "success_data": success_data})
