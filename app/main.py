from fastapi.staticfiles import StaticFiles

from create_app import app
from routers.auth import router as auth_router
from routers.index import router as index_router
from routers.edit_texts import router as edit_texts_router
from routers.mailing import router as mailing_router

app.include_router(auth_router)
app.include_router(index_router)
app.include_router(edit_texts_router)
app.include_router(mailing_router)


app.mount("/static", StaticFiles(directory="static"), name="static")
