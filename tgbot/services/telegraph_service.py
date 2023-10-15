import json
import sys
from typing import List, Optional

import aiofiles
import aiohttp
from telegraph.utils import HtmlToNodesParser

from tgbot.models.sql_connector import UsersDAO


class TelegraphCreatePage:

    @staticmethod
    async def __upload_files(file_name: str) -> str:
        async with aiofiles.open(file_name, "rb") as file:
            url = "https://telegra.ph/upload"
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('file', file, filename='file')
                async with session.post(url=url, data=data, timeout=100) as resp:
                    resp = await resp.json()
        return f'https://telegra.ph{resp[0]["src"]}'

    @staticmethod
    async def __get_or_create_token(user_id: str | int, author_name: str) -> str:
        user = await UsersDAO.get_one_or_none(user_id=str(user_id))
        if user["telegraph_token"]:
            return user["telegraph_token"]
        async with aiohttp.ClientSession() as session:
            url = "https://api.telegra.ph/createAccount"
            params = dict(short_name=author_name, author_name=author_name)
            async with session.get(url=url, params=params, timeout=100) as resp:
                resp = await resp.json()
                await UsersDAO.update_by_user_id(user_id=str(user_id), telegraph_token=resp["result"]["access_token"])
                return resp["result"]["access_token"]

    @staticmethod
    async def __create_page_request(token: str, title: str, author_name: str, content: List[dict]) -> str:
        async with aiohttp.ClientSession() as session:
            url = "https://api.telegra.ph/createPage"
            params = dict(
                access_token=token,
                title=title,
                author_name=author_name,
                content=content,
                return_content="true"
            )
            async with session.get(url=url, params=params, timeout=100) as resp:
                resp = await resp.json()
                return resp["result"]["url"]

    @staticmethod
    def html_to_nodes(html_content):
        parser = HtmlToNodesParser()
        parser.feed(html_content)
        return parser.get_nodes()

    @classmethod
    async def create_page(
            cls,
            user_id: str | int,
            album_photos: List[str],
            layout_photo: str,
            # description: str,
            calc_photo: str,
            author: Optional[str]
    ) -> str:
        content = []
        for photo in album_photos:
            photo_url = await cls.__upload_files(file_name=photo)
            content.append(f'<figure><img src="{photo_url}"><figcaption>Фото объекта</figcaption></figure>')
        layout_url = await cls.__upload_files(file_name=layout_photo)
        calc_url = await cls.__upload_files(file_name=calc_photo)
        content_extend = [
            "<br>",
            f'<figure><img src="{layout_url}"><figcaption>Layout</figcaption></figure>',
            # "<br>"
            # f"<p>{description}</p>",
            "<br>"
            f'<figure><img src="{calc_url}"><figcaption>Calculation</figcaption></figure>'
        ]
        content.extend(content_extend)
        content = cls.html_to_nodes(html_content="\n".join(content))
        content = json.dumps(content)
        author_name = author if author else "Author"
        token = await cls.__get_or_create_token(user_id=user_id, author_name=author_name)
        bytes_count = sys.getsizeof(content)
        print(bytes_count)
        page = await cls.__create_page_request(
            token=token,
            title="Commercial proposal",
            author_name=author_name,
            content=content
        )
        return page
