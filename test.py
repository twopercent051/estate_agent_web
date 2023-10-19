import csv
from typing import List

from openpyxl.workbook import Workbook


def get_csv():
    with open("result.csv", encoding="utf-8") as r_file:
        file_reader = csv.reader(r_file, delimiter=";")
        count = 0
        result = []
        phones = []
        for row in file_reader:
            count += 1
            phone = row[2]
            if phone == "":
                phone = row[3]
                if len(phone) > 0:
                    if phone[0] == "9":
                        phone = f"+{phone}"
                    if phone[0] == "0":
                        phone = f"+971{phone[1:]}"
            if phone not in phones:
                result.append([row[0], row[1], phone])
            phones.append(phone)
            # if count == 100:
            #     break
    print(count)
    return result


def create_xlsx(data: List[list]):
    wb = Workbook()
    ws = wb.active
    for row in data:

        ws.append(
            (
                row[0],
                row[1],
                row[2],
            )
        )
    wb.save("result.xlsx")


def main():
    data = get_csv()
    create_xlsx(data)


if __name__ == "__main__":
    main()
