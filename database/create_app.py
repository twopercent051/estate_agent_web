import logging
import betterlogging as bl

from fastapi import FastAPI

from config import load_config

app = FastAPI(title="estate_agent_database")

config = load_config(".env")

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)
