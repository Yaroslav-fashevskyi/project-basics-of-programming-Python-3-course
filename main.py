import datetime
import json
import uuid
import sys
from typing import List, Dict, Optional

DATA_FILE = "personnel_data.json"


class Position:
    ALLOWED_ACCESS_LEVELS = [1, 2, 3, 4, 5]

    def __init__(
        self,
        name: str,
        access_level: int = 1,
        salary: float = 0.0,
        id: Optional[str] = None
    ):
        # Генеруємо id, якщо не передали
        self.id = id or str(uuid.uuid4())
        self.name = name.strip()
        self.access_level = access_level
        self.salary = salary

        # Валідація
        if not self.name:
            raise ValueError("Назва посади не може бути порожньою.")
        if self.access_level not in Position.ALLOWED_ACCESS_LEVELS:
            raise ValueError(f"Рівень доступу має бути одним із {Position.ALLOWED_ACCESS_LEVELS}.")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "access_level": self.access_level,
            "salary": self.salary,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Position":
        return cls(
            name=data.get("name", ""),
            access_level=data.get("access_level", 1),
            salary=data.get("salary", 0.0),
            id=data.get("id")
        )

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id}) – Рівень {self.access_level}, Зарплата {self.salary:.2f}"


class Employee:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        position: Position,
        hire_date: datetime.date,
        id: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.hire_date = hire_date

        # Валідація імені та прізвища
        if not self.validate_name(self.first_name):
            raise ValueError("Ім'я має містити лише літери та починатися з великої літери.")
        if not self.validate_name(self.last_name):
            raise ValueError("Прізвище має містити лише літери та починатися з великої літери.")
        # Дата не в майбутньому
        if self.hire_date > datetime.date.today():
            raise ValueError("Дата прийняття не може бути в майбутньому.")

    @staticmethod
    def validate_name(name: str) -> bool:
        return name.isalpha() and name[0].isupper()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "position_id": self.position.id,
            "hire_date": self.hire_date.isoformat(),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict,
        positions: Dict[str, Position]
    ) -> Optional["Employee"]:
        # парсимо дату
        try:
            hd = datetime.datetime.strptime(data.get("hire_date", ""), "%Y-%m-%d").date()
        except Exception:
            print(f"Некоректна дата для співробітника {data.get('first_name','?')} {data.get('last_name','?')}")
            return None
        # шукаємо об’єкт Position
        pos = positions.get(data.get("position_id"))
        if not pos:
            print(f"Посада з ID {data.get('position_id')} не знайдена для {data.get('first_name')} {data.get('last_name')}")
            return None
        return cls(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            position=pos,
            hire_date=hd,
            id=data.get("id")
        )

    def __str__(self) -> str:
        return (
            f"{self.first_name} {self.last_name} (ID: {self.id}) | "
            f"{self.position.name} | Прийнятий: {self.hire_date.isoformat()}"
        )


class Payroll:
    """Обробка зарплатних розрахунків"""
    PDFO_RATE = 0.18
    MILITARY_TAX = 0.015

    @staticmethod
    def calculate_net(gross: float) -> float:
        rate = Payroll.PDFO_RATE + Payroll.MILITARY_TAX
        return round(gross * (1 - rate), 2)

    @staticmethod
    def summary(employees: List[Employee]) -> Dict:
        gross_list = [e.position.salary for e in employees]
        net_list = [Payroll.calculate_net(g) for g in gross_list]
        return {
            "total_gross": sum(gross_list),
            "total_net": sum(net_list),
            "average_gross": sum(gross_list) / len(gross_list) if gross_list else 0,
            "average_net": sum(net_list) / len(net_list) if net_list else 0,
        }


class PersonnelManager:
    """Управління посадами та співробітниками"""
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
                        id=pid
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
        emp = Employee(first_name=first, last_name=last,
                       position=self.positions[pos_id], hire_date=hire)
        self.employees.append(emp)
        self.save_data()
        print(f"Додано співробітника: {emp}")

    def update_employee(self, emp_id: str, **kwargs):
        for e in self.employees:
            if e.id == emp_id:
                if "first_name" in kwargs and Employee.validate_name(kwargs["first_name"]):
                    e.first_name = kwargs["first_name"]
                if "last_name" in kwargs and Employee.validate_name(kwargs["last_name"]):
                    e.last_name = kwargs["last_name"]
                if "position_id" in kwargs and kwargs["position_id"] in self.positions:
                    e.position = self.positions[kwargs["position_id"]]
                if "hire_date" in kwargs and kwargs["hire_date"] <= datetime.date.today():
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

    def list_employees(self, sort_by: str = "last_name", filter_by: Dict = None):
        emps = list(self.employees)
        if filter_by:
            for key, val in filter_by.items():
                if key == "position_name":
                    emps = [e for e in emps if e.position.name == val]
                if key == "hire_year":
                    emps = [e for e in emps if e.hire_date.year == val]
        if sort_by == "last_name":
            emps.sort(key=lambda e: e.last_name)
        elif sort_by == "position":
            emps.sort(key=lambda e: e.position.name)
        elif sort_by == "hire_date":
            emps.sort(key=lambda e: e.hire_date)
        print("\n--- Список співробітників ---")
        for e in emps:
            print(e)

    def search_employees(self, query: str):
        found = [
            e for e in self.employees
            if query.lower() in e.first_name.lower() or query.lower() in e.last_name.lower()
        ]
        print(f"\nЗнайдено {len(found)} співробітників за запитом '{query}':")
        for e in found:
            print(e)

    def payroll_info(self):
        print("\n--- Зарплатна відомість ---")
        summary = Payroll.summary(self.employees)
        for e in self.employees:
            gross = e.position.salary
            net = Payroll.calculate_net(gross)
            print(f"{e.first_name} {e.last_name} | Брутто: {gross:.2f} | Нетто: {net:.2f}")
        print("\n--- Загальні показники ---")
        for k, v in summary.items():
            print(f"{k.replace('_', ' ').capitalize()}: {v:.2f}")


def input_date(prompt: str) -> datetime.date:
    while True:
        val = input(prompt)
        try:
            return datetime.datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            print("Невірний формат. Використовуйте YYYY-MM-DD.")


def main():
    mgr = PersonnelManager()
    while True:
        print("\n=== Меню ===")
        print("1. Управління посадами")
        print("2. Управління співробітниками")
        print("3. Пошук співробітників")
        print("4. Зарплата та звіти")
        print("5. Вийти")
        ch = input("Вибір: ")
        if ch == "1":
            print("a) Додати посаду\nb) Оновити посаду\nc) Видалити посаду\nd) Показати всі посади")
            sub = input("Вибір: ")
            if sub == "a":
                try:
                    name = input("Назва: ")
                    lvl = int(input("Рівень (1-5): "))
                    sal = float(input("Зарплата: "))
                    mgr.add_position(name, lvl, sal)
                except Exception as e:
                    print("Помилка:", e)
            elif sub == "b":
                for p in mgr.positions.values():
                    print(p)
                pid = input("ID посади: ")
                name = input("Нова назва (Enter щоб пропустити): ")
                lvl = input("Новий рівень (1-5) (Enter щоб пропустити): ")
                sal = input("Нова зарплата (Enter щоб пропустити): ")
                kwargs = {}
                if name:
                    kwargs['name'] = name
                if lvl:
                    kwargs['access_level'] = int(lvl)
                if sal:
                    kwargs['salary'] = float(sal)
                mgr.update_position(pid, **kwargs)
            elif sub == "c":
                for p in mgr.positions.values():
                    print(p)
                mgr.delete_position(input("ID посади для видалення: "))
            elif sub == "d":
                for p in mgr.positions.values():
                    print(p)

        elif ch == "2":
            print("a) Додати співробітника\nb) Оновити співробітника\nc) Видалити співробітника\nd) Показати співробітників зі сортуванням")
            sub = input("Вибір: ")
            if sub == "a":
                try:
                    first = input("Ім'я: ")
                    last = input("Прізвище: ")
                    for p in mgr.positions.values():
                        print(p)
                    pid = input("ID посади: ")
                    hd = input_date("Дата прийняття (YYYY-MM-DD): ")
                    mgr.add_employee(first, last, pid, hd)
                except Exception as e:
                    print("Помилка:", e)
            elif sub == "b":
                mgr.list_employees()
                eid = input("ID співробітника: ")
                fn = input("Нове ім'я (Enter щоб пропустити): ")
                ln = input("Нове прізвище (Enter щоб пропустити): ")
                new_hd = input("Нова дата (YYYY-MM-DD) (Enter щоб пропустити): ")
                hd = None
                if new_hd:
                    hd = datetime.datetime.strptime(new_hd, "%Y-%m-%d").date()
                for p in mgr.positions.values():
                    print(p)
                npid = input("Новий ID посади (Enter щоб пропустити): ")
                kwargs = {}
                if fn:
                    kwargs['first_name'] = fn
                if ln:
                    kwargs['last_name'] = ln
                if hd:
                    kwargs['hire_date'] = hd
                if npid:
                    kwargs['position_id'] = npid
                mgr.update_employee(eid, **kwargs)
            elif sub == "c":
                mgr.list_employees()
                mgr.delete_employee(input("ID співробітника для видалення: "))
            elif sub == "d":
                print("Сортувати за: 1-прізвище, 2-посада, 3-дата прийняття")
                opt = input("Вибір: ")
                key = (
                    "last_name" if opt == "1" else
                    "position" if opt == "2" else
                    "hire_date" if opt == "3" else
                    "last_name"
                )
                mgr.list_employees(sort_by=key)

        elif ch == "3":
            q = input("Пошуковий запит (ім'я чи прізвище): ")
            mgr.search_employees(q)

        elif ch == "4":
            mgr.payroll_info()

        elif ch == "5":
            print("Вихід...")
            sys.exit(0)

        else:
            print("Невірний вибір. Спробуйте знову.")


if __name__ == "__main__":
    main()
