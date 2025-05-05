import json
import datetime
from typing import Dict, List
from position import Position
from employee import Employee
from payroll import Payroll
from utils import DATA_FILE


class PersonnelManager:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.employees: List[Employee] = []
        self.load_data()

    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Підтримка двох форматів JSON: словник або список
            raw_positions = data.get("positions", [])
            if isinstance(raw_positions, dict):
                for pid, info in raw_positions.items():
                    pos = Position(
                        name=info.get("name", ""),
                        access_level=info.get("access_level", 1),
                        salary=info.get("salary", 0.0),
                        id=pid,
                    )
                    self.positions[pid] = pos
            elif isinstance(raw_positions, list):
                for info in raw_positions:
                    pos = Position.from_dict(info)
                    self.positions[pos.id] = pos
            # Завантаження співробітників
            raw_emps = data.get("employees", [])
            for info in raw_emps:
                emp = Employee.from_dict(info, self.positions)
                if emp:
                    self.employees.append(emp)
        except FileNotFoundError:
            self.save_data()

    def save_data(self):
        data = {
            "positions": [p.to_dict() for p in self.positions.values()],
            "employees": [e.to_dict() for e in self.employees],
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # --- Position Methods ---
    def add_position(self, name: str, access_level: int, salary: float):
        if any(p.name == name for p in self.positions.values()):
            raise ValueError("Посада з такою назвою вже існує.")
        pos = Position(name=name, access_level=access_level, salary=salary)
        self.positions[pos.id] = pos
        self.save_data()
        print(f"Додано посаду: {pos}")

    def update_position(self, pos_id: str, **kwargs):
        pos = self.positions.get(pos_id)
        if not pos:
            print("Посада не знайдена.")
            return
        pos.name = kwargs.get("name", pos.name)
        pos.access_level = kwargs.get("access_level", pos.access_level)
        pos.salary = kwargs.get("salary", pos.salary)
        self.save_data()
        print(f"Оновлено посаду: {pos}")

    def delete_position(self, pos_id: str):
        if any(e.position.id == pos_id for e in self.employees):
            print("Не можна видалити посаду, поки є співробітники з нею.")
            return
        if self.positions.pop(pos_id, None):
            self.save_data()
            print(f"Посаду {pos_id} видалено.")
        else:
            print("Посада не знайдена.")

    # --- Employee Methods ---
    def add_employee(self, first: str, last: str, pos_id: str, hire: datetime.date):
        if pos_id not in self.positions:
            raise ValueError("Вказано невірний ID посади.")
        emp = Employee(
            first_name=first,
            last_name=last,
            position=self.positions[pos_id],
            hire_date=hire,
        )
        self.employees.append(emp)
        self.save_data()
        print(f"Додано співробітника: {emp}")

    def update_employee(self, emp_id: str, **kwargs):
        for e in self.employees:
            if e.id == emp_id:
                if "first_name" in kwargs and Employee.validate_name(
                    kwargs["first_name"]
                ):
                    e.first_name = kwargs["first_name"]
                if "last_name" in kwargs and Employee.validate_name(
                    kwargs["last_name"]
                ):
                    e.last_name = kwargs["last_name"]
                if "position_id" in kwargs and kwargs["position_id"] in self.positions:
                    e.position = self.positions[kwargs["position_id"]]
                if (
                    "hire_date" in kwargs
                    and kwargs["hire_date"] <= datetime.date.today()
                ):
                    e.hire_date = kwargs["hire_date"]
                self.save_data()
                print(f"Оновлено співробітника: {e}")
                return
        print("Співробітника не знайдено.")

    def delete_employee(self, emp_id: str):
        before = len(self.employees)
        self.employees = [e for e in self.employees if e.id != emp_id]
        if len(self.employees) < before:
            self.save_data()
            print(f"Співробітника {emp_id} видалено.")
        else:
            print("Співробітника не знайдено.")

    def list_employees(self, sort_by: str = "last_name") -> List[Employee]:
        """Повертає список співробітників, відсортований за sort_by."""
        valid = {"last_name", "position", "hire_date"}
        if sort_by not in valid:
            sort_by = "last_name"

        if sort_by == "position":
            # сортуємо за назвою посади
            key_fn = lambda e: e.position.name.lower()
        else:
            # сортуємо за атрибутом employee.last_name або employee.hire_date
            key_fn = lambda e: getattr(e, sort_by)

        return sorted(self.employees, key=key_fn)

    def search_employees(self, query: str):
        found = [
            e
            for e in self.employees
            if query.lower() in e.first_name.lower()
            or query.lower() in e.last_name.lower()
        ]
        print(f"\nЗнайдено {len(found)} співробітників за запитом '{query}':")
        return found

    def payroll_info(self):
        print("\n--- Зарплатна відомість ---")
        summary = Payroll.summary(self.employees)
        for e in self.employees:
            gross = e.position.salary
            net = Payroll.calculate_net(gross)
            print(
                f"{e.first_name} {e.last_name} | Брутто: {gross:.2f} | Нетто: {net:.2f}"
            )
        print("\n--- Загальні показники ---")
        for k, v in summary.items():
            print(f"{k.replace('_', ' ').capitalize()}: {v:.2f}")
