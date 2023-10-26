from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette import status
from starlette.responses import RedirectResponse

from api_models.redis_connector import AppRedisConnector
from create_app import templates, app
from routers.auth import SUserAuth, get_current_user
from texts_config import config_texts, config_languages

router = APIRouter()


@router.get("/edit_texts", response_class=HTMLResponse)
async def edit_texts_menu(request: Request, user: SUserAuth = Depends(get_current_user)):
    modules = []
    for key in config_texts:
        modules.append(dict(href=key, title=config_texts[key]["title"]))
    return templates.TemplateResponse("edit_texts.html", {"request": request, "texts": modules})


@router.get("/edit_txt/{module}", response_class=HTMLResponse)
async def edit_text_module(request: Request, module: str, user: SUserAuth = Depends(get_current_user)):
    module_title = config_texts[module]["title"]
    handlers = []
    for key in config_texts[module]["handlers"]:
        handler_texts = []
        handler_buttons = []
        handler = config_texts[module]["handlers"][key]
        handler_title = handler["title"]
        for lang in config_languages:
            handler_text = AppRedisConnector.get_text_by_lang(lang=lang, module=module, handler=key)
            text_data = dict(handler_title=handler_title, lang=lang, handler_text=handler_text)
            handler_texts.append(text_data)
            if "buttons" in handler:
                for button in handler["buttons"]:
                    button_title = handler["buttons"][button]
                    button_text = AppRedisConnector.get_text_by_lang(lang=lang, module=module, handler=key, obj=button)
                    button_data = dict(lang=lang, clb_data=button, button_text=button_text, button_title=button_title)
                    handler_buttons.append(button_data)
        handler_data = dict(handler_title=handler_title,
                            handler_clb=key,
                            handler_texts=handler_texts,
                            handler_buttons=handler_buttons)
        handlers.append(handler_data)
    return templates.TemplateResponse("edit_module.html", {"request": request,
                                                           "module": module,
                                                           "module_title": module_title,
                                                           "handlers": handlers})


@router.post("/save_text", response_class=HTMLResponse)
async def save_text(request: Request, user: SUserAuth = Depends(get_current_user)):
    form_data = await request.form()
    for text in form_data.multi_items():
        if text[1] != "":
            text_id_list = text[0].split(":")
            module = text_id_list[0]
            handler = text_id_list[1]
            obj = text_id_list[2]
            lang = text_id_list[3]
            AppRedisConnector.update_text(lang=lang, module=module, handler=handler, obj=obj, text=text[1])
    return RedirectResponse(url=app.url_path_for("edit_texts_main_menu"), status_code=status.HTTP_303_SEE_OTHER)
