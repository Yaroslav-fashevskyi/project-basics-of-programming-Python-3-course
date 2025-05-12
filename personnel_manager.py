import json
import datetime
import uuid
from typing import Dict, List, Optional
from position import Position
from employee import Employee
from payroll import Payroll
from utils import DATA_FILE


class PersonnelManager:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.employees: List[Employee] = []
        self.load_data()

    def load_data(self) -> None:
        # Завантажує дані з файлу
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.save_data()
            return

        # Посади
        for raw in data.get("positions", []):
            pos = Position.from_dict(raw)
            self.positions[pos.id] = pos
        # Працівники
        for raw in data.get("employees", []):
            emp = Employee.from_dict(raw, self.positions)
            if emp:
                self.employees.append(emp)

    def save_data(self) -> None:
        # Зберігає дані в файл
        data = {
            "positions": [p.to_dict() for p in self.positions.values()],
            "employees": [e.to_dict() for e in self.employees],
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # --- Position Methods ---
    def add_position(self, name: str, access_level: int, salary: float) -> None:
        # Унікальність назви
        if any(p.name.lower() == name.lower() for p in self.positions.values()):
            raise ValueError("Посада з такою назвою вже існує.")
        pos = Position(name=name, access_level=access_level, salary=salary)
        self.positions[pos.id] = pos
        self.save_data()
        print(f"Додано посаду: {pos}")

    def delete_position(self, pos_id: str) -> None:
        if any(e.position.id == pos_id for e in self.employees):
            raise ValueError("Неможливо видалити: до посади прив'язані співробітники.")
        if pos_id not in self.positions:
            raise ValueError("Посада з таким ID не знайдена.")
        del self.positions[pos_id]
        self.save_data()
        print(f"Посаду {pos_id} видалено.")

    def update_position(
        self,
        pos_id: str,
        name: Optional[str] = None,
        access_level: Optional[int] = None,
        salary: Optional[float] = None,
    ) -> None:
        # Оновлює назву, рівень доступу та зарплату
        if pos_id not in self.positions:
            raise ValueError("Посада з таким ID не знайдена.")
        pos = self.positions[pos_id]
        if name:
            if any(
                p.name.lower() == name.lower() and p.id != pos_id
                for p in self.positions.values()
            ):
                raise ValueError("Назва посади має бути унікальною.")
            pos.name = name
        if access_level is not None:
            if access_level not in Position.ALLOWED_ACCESS_LEVELS:
                raise ValueError("Неправильний рівень доступу.")
            pos.access_level = access_level
        if salary is not None:
            pos.salary = salary
        self.save_data()
        print(f"Оновлено посаду: {pos}")

    # --- Employee Methods ---
    def add_employee(
        self,
        first_name: str,
        last_name: str,
        position_id: str,
        hire_date: datetime.date,
    ) -> None:
        if not Employee.validate_name(first_name) or not Employee.validate_name(
            last_name
        ):
            raise ValueError(
                "Ім'я та прізвище повинні містити лише літери та починатися з великої."
            )
        if hire_date > datetime.date.today():
            raise ValueError("Дата прийняття не може бути в майбутньому.")
        if position_id not in self.positions:
            raise ValueError("Посада з таким ID не знайдена.")
        emp = Employee(
            first_name=first_name,
            last_name=last_name,
            position=self.positions[position_id],
            hire_date=hire_date,
        )
        self.employees.append(emp)
        self.save_data()
        print(f"Додано співробітника: {emp}")

    def delete_employee(self, emp_id: str) -> None:
        before = len(self.employees)
        self.employees = [e for e in self.employees if e.id != emp_id]
        if len(self.employees) == before:
            raise ValueError("Співробітника з таким ID не знайдено.")
        self.save_data()
        print(f"Співробітника {emp_id} видалено.")

    def update_employee(self, emp_id: str, **kwargs) -> None:
        # Оновлює імя, прізвище, посаду, дату прийняття
        for e in self.employees:
            if e.id == emp_id:
                if "first_name" in kwargs:
                    if Employee.validate_name(kwargs["first_name"]):
                        e.first_name = kwargs["first_name"]
                    else:
                        raise ValueError("Невірний формат імені.")
                if "last_name" in kwargs:
                    if Employee.validate_name(kwargs["last_name"]):
                        e.last_name = kwargs["last_name"]
                    else:
                        raise ValueError("Невірний формат прізвища.")
                if "position_id" in kwargs:
                    pid = kwargs["position_id"]
                    if pid in self.positions:
                        e.position = self.positions[pid]
                    else:
                        raise ValueError("Посада з таким ID не знайдена.")
                if "hire_date" in kwargs:
                    hd = kwargs["hire_date"]
                    if hd <= datetime.date.today():
                        e.hire_date = hd
                    else:
                        raise ValueError("Дата прийняття не може бути в майбутньому.")
                self.save_data()
                print(f"Оновлено співробітника: {e}")
                return
        raise ValueError("Співробітника з таким ID не знайдено.")

    def list_employees(self, sort_by: str = "last_name") -> List[Employee]:
        # Повертає відсортований список співробітників
        opts = {"last_name", "position", "hire_date"}
        key = sort_by if sort_by in opts else "last_name"
        if key == "position":
            return sorted(self.employees, key=lambda e: e.position.name.lower())
        return sorted(self.employees, key=lambda e: getattr(e, key))

    def search_employees(self, query: str) -> List[Employee]:
        return [
            e
            for e in self.employees
            if query.lower() in e.first_name.lower()
            or query.lower() in e.last_name.lower()
        ]

    def payroll_info(self) -> None:
        print("--- Зарплатна відомість ---")
        summary = Payroll.summary(self.employees)
        for e in self.employees:
            gross = e.position.salary
            net = Payroll.calculate_net(gross)
            print(f"{e.first_name} {e.last_name}: брутто={gross:.2f}, нетто={net:.2f}")
        print("--- Загальні показники ---")
        for k, v in summary.items():
            print(f"{k.replace('_',' ').capitalize()}: {v:.2f}")
