from dataclasses import dataclass

from environs import Env


@dataclass
class TgBotConfig:
    bot_token: str
    admins: list


@dataclass
class AuthConfig:
    login: str
    password: str
    secret_key: str
    algorithm: str


@dataclass
class DbConfig:
    url: str


@dataclass
class Config:
    tg_bot: TgBotConfig
    db: DbConfig
    auth: AuthConfig


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBotConfig(
            bot_token=env.str("BOT_TOKEN"),
            admins=env.list("ADMINS")
        ),
        db=DbConfig(
            url=env.str("DB_URL")
        ),
        auth=AuthConfig(
            login=env.str("LOGIN"),
            password=env.str("PASS"),
            secret_key=env.str("SECRET_KEY"),
            algorithm=env.str("ALGORITHM"),
        ),
    )
