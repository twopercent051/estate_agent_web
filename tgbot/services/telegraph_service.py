from typing import List, Optional

import requests
from telegraph import Telegraph

from create_bot import config

token = config.tg_bot.telegraph_token
telegraph = Telegraph(token)


class TelegraphCreatePage:

    @staticmethod
    def __upload_files(file_name: str) -> str:
        with open(file_name, "rb") as file:
            url = "https://telegra.ph/upload"
            response = requests.post(url, files={"file": ("file", file)}, timeout=1)
        return f'https://telegra.ph{response.json()[0]["src"]}'

    @classmethod
    def create_page(cls, album_photos: List[str], calc_photo: str, author: Optional[str]) -> str:
        album_urls = []
        for photo in album_photos:
            photo_url = cls.__upload_files(file_name=photo)
            album_urls.append(photo_url)
            print(photo_url)
        calc_url = cls.__upload_files(file_name=calc_photo)
        print(calc_url)
        content = ["<p>Фото объекта:</p>"]
        for photo in album_urls:
            content.append(f'<img src="{photo}">')
        content.extend(
            [
                "<p>Расчёты:</p>",
                f'<img src="{calc_url}">'
            ]
        )
        response = telegraph.create_page(title="Коммерческое предложение",
                                         html_content="\n".join(content),
                                         author_name=author)
        return f"https://telegra.ph/{response['path']}"
