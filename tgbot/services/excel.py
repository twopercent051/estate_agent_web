from datetime import datetime
from typing import Optional, List

from openpyxl import Workbook
from openpyxl.styles import Font
import os


class ExcelFile:
    def __init__(self):
        self.users_path = f"{os.getcwd()}/users_list.xlsx"

    @staticmethod
    def __reformat_date(date: Optional[datetime]) -> str:
        result = date.strftime("%d-%m-%Y %H:%M") if date else "---"
        return result

    def create_users_file(self, users: List[dict]):
        wb = Workbook()
        ws = wb.active
        ws.append(
            (
                "User ID",
                "Username",
                "Дата регистрации (utc)"
                "Количество запросов"
            )
        )
        title_ft = Font(bold=True)
        for row in ws['A1:T1']:
            for cell in row:
                cell.font = title_ft

        for user in users:
            ws.append(
                (
                    user["user_id"],
                    user["username"],
                    self.__reformat_date(user["create_dtime"]),
                    user["request_count"],
                )
            )
        wb.save(self.users_path)
