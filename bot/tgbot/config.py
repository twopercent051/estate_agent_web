from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    url: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    admin_group: str
    # use_redis: bool
    check_chat_id: str


@dataclass
class Miscellaneous:
    pass


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            admin_group=env.str('ADMIN_GROUP'),
            check_chat_id=env.str("CHECK_CHAT_ID"),
        ),
        db=DbConfig(
            url=env.str('DB_URL'),
        ),
        misc=Miscellaneous()
    )
