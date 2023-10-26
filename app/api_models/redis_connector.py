import requests

from create_app import DB_URL


class AppRedisConnector:

    @staticmethod
    def __post_request(route: str, data: dict = None):
        url = f"{DB_URL}/redis/{route}"
        ret = requests.post(url=url, params=data)
        return ret.json()

    @classmethod
    def get_user_lang(cls, user_id: str | int = None, all_dict: bool = False) -> str | dict:
        data = dict(user_id=user_id, all_dict=all_dict)
        return cls.__post_request(route="get_user_lang", data=data)

    @classmethod
    def update_user_lang(cls, user_id: str | int, lang: str):
        data = dict(user_id=user_id, lang=lang)
        return cls.__post_request(route="update_user_lang", data=data)

    @classmethod
    def get_user_text(cls, user_id: str | int, module: str, handler: str, obj: str = "text") -> str:
        data = dict(user_id=user_id, module=module, handler=handler, obj=obj)
        return cls.__post_request(route="get_user_text", data=data)

    @classmethod
    def get_text_by_lang(cls, lang: str, module: str, handler: str, obj: str = "text") -> str:
        data = dict(lang=lang, module=module, handler=handler, obj=obj)
        return cls.__post_request(route="get_text_by_lang", data=data)

    @classmethod
    def update_text(cls, lang: str, module: str, handler: str, obj: str, text: str):
        data = dict(lang=lang, module=module, handler=handler, obj=obj, text=text)
        return cls.__post_request(route="update_text", data=data)

    @classmethod
    def get_tlg_code(cls) -> dict:
        return cls.__post_request(route="get_tlg_code")

    @classmethod
    def set_tlg_code(cls, code: str):
        data = dict(code=code)
        return cls.__post_request(route="set_tlg_code", data=data)
