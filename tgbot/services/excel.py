from datetime import datetime
from typing import Optional, List

from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Font
import os


class ExcelFile:
    def __init__(self):
        self.price_path = f"{os.getcwd()}/price_list.xlsx"
        self.shipments_path = f"{os.getcwd()}/shipments_list.xlsx"

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
                    user["user_id"],
                )
            )
        wb.save(self.shipments_path)