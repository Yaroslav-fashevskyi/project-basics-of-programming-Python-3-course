import datetime

DATA_FILE = "personnel_data.json"


def input_date(prompt: str) -> datetime.date:
    while True:
        val = input(prompt)
        try:
            return datetime.datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            print("Невірний формат. Використовуйте YYYY-MM-DD.")
