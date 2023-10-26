import logging
import os
import betterlogging as bl

from fastapi import FastAPI
from starlette.templating import Jinja2Templates

from config import load_config

app = FastAPI(title="Estate_Agent_CRM")

templates = Jinja2Templates(directory=f"{os.getcwd()}/templates")
config = load_config(".env")

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)

DB_URL = config.db.url
