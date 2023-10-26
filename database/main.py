from create_app import app
from models.redis_connector import ModelRedisConnector
from routers.sql.users_sql_router import router as users_sql_router
from routers.sql.files_sql_router import router as files_sql_router
from routers.redis.redis_router import router as redis_router


app.include_router(users_sql_router)
app.include_router(files_sql_router)
app.include_router(redis_router)


@app.on_event("startup")
async def on_startup():
    await ModelRedisConnector.redis_start()
