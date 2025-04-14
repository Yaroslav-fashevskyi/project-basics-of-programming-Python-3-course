import datetime
import json
import uuid

DATA_FILE = "personnel_data.json"  # Файл для збереження даних


# Клас Position – представляє посаду в компанії
class Position:
    """
    Атрибути:
      id: Унікальний ідентифікатор посади.
      name: Назва посади.
      access_level: Рівень доступу (від 1 до 5)
          - 1: Найнижчий рівень (базовий доступ, обмежені операції).
          - 5: Найвищий рівень (повний доступ, адміністративні права).
      salary: Зарплата для посади.
    """
    ALLOWED_ACCESS_LEVELS = [1, 2, 3, 4, 5]

    def __init__(self, name: str, access_level: int, salary: float, id: str = None):
        if access_level not in Position.ALLOWED_ACCESS_LEVELS:
            raise ValueError(
                f"Рівень доступу має бути одним із {Position.ALLOWED_ACCESS_LEVELS}. "
                "Рівень 1 – найнижчий, 5 – найвищий."
            )
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.access_level = access_level
        self.salary = salary

    def __str__(self):
        return f"ID: {self.id} | Посада: {self.name}, Рівень: {self.access_level}, Зарплата: {self.salary}"


# Клас Employee – представляє співробітника
class Employee:
    def __init__(self, first_name: str, last_name: str, position: Position, hire_date: datetime.date, id: str = None):
        # Перевірка, що ім'я та прізвище складаються лише з літер та починаються з великої літери.
        if not Employee.validate_name(first_name):
            raise ValueError("Ім'я має містити лише літери та починатися з великої літери.")
        if not Employee.validate_name(last_name):
            raise ValueError("Прізвище має містити лише літери та починатися з великої літери.")
        # Дата прийняття не може бути в майбутньому.
        if hire_date > datetime.date.today():
            raise ValueError("Дата прийняття не може бути в майбутньому.")
        self.id = id if id is not None else str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.hire_date = hire_date

    def __str__(self):
        return f"ID: {self.id} | {self.first_name} {self.last_name} | {self.position.name} | Прийнятий: {self.hire_date}"

    @staticmethod
    def validate_name(name: str) -> bool:
        return name.isalpha() and name[0].isupper()


# Клас Payroll – розраховує чисту зарплату з урахуванням податків:
# 18% ПДФО + 1.5% військовий збір (разом 19.5%).
class Payroll:
    PDGO_RATE = 0.18      # Податок на доходи фізичних осіб
    MILITARY_TAX = 0.015  # Військовий збір

    @staticmethod
    def calculate_net_salary(gross_salary: float) -> float:
        total_tax_rate = Payroll.PDGO_RATE + Payroll.MILITARY_TAX  # 19.5%
        return gross_salary * (1 - total_tax_rate)

    @staticmethod
    def display_payroll(employees: list):
        print("\n--- Зарплатна відомість ---")
        for emp in employees:
            gross = emp.position.salary
            net = Payroll.calculate_net_salary(gross)
            print(f"{emp.first_name} {emp.last_name} | {emp.position.name} | Брутто: {gross}, Нетто: {net:.2f}")


# Клас PersonnelManager – управляє співробітниками та посадами, зберігає дані у JSON.
class PersonnelManager:
    def __init__(self):
        self.employees = []
        # Посади зберігаються у словнику, ключ – унікальний id.
        self.positions = {}
        self.load_data()

    def save_data(self):
        """Зберігає дані про посади та співробітників у JSON-файл."""
        data = {
            "positions": {},
            "employees": []
        }
        # Збереження посад: ключ – id посади.
        for pos_id, pos in self.positions.items():
            data["positions"][pos_id] = {
                "name": pos.name,
                "access_level": pos.access_level,
                "salary": pos.salary
            }
        # Збереження співробітників: зберігаємо їх id та id посади.
        for emp in self.employees:
            data["employees"].append({
                "id": emp.id,
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "position_id": emp.position.id,
                "hire_date": emp.hire_date.isoformat()
            })
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        """Завантажує дані з JSON-файлу, або створює новий, якщо файла немає."""
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Завантаження посад.
            positions_data = data.get("positions", {})
            for pos_id, pos_info in positions_data.items():
                # Перевірка наявності необхідних ключів
                if "name" not in pos_info or "access_level" not in pos_info or "salary" not in pos_info:
                    print(f"Некоректний запис для позиції з ID {pos_id}: {pos_info}")
                    continue
                pos = Position(pos_info["name"], pos_info["access_level"], pos_info["salary"], id=pos_id)
                self.positions[pos_id] = pos
            # Завантаження співробітників.
            employees_data = data.get("employees", [])
            for emp_data in employees_data:
                try:
                    hire_date = datetime.datetime.strptime(emp_data["hire_date"], "%Y-%m-%d").date()
                except (KeyError, ValueError):
                    print(f"Некоректна дата для співробітника {emp_data.get('first_name', '?')} {emp_data.get('last_name', '?')}")
                    continue
                pos_id = emp_data.get("position_id")
                if pos_id in self.positions:
                    emp = Employee(
                        emp_data["first_name"],
                        emp_data["last_name"],
                        self.positions[pos_id],
                        hire_date,
                        id=emp_data["id"]
                    )
                    self.employees.append(emp)
                else:
                    print(f"Посада з ID {pos_id} для співробітника {emp_data.get('first_name', '?')} {emp_data.get('last_name', '?')} не знайдена.")
        except FileNotFoundError:
            # Якщо файл не знайдено, створюємо його з порожніми даними.
            self.save_data()

    def add_position(self, name: str, access_level: int, salary: float) -> None:
        # Перевірка унікальності назви посади.
        for pos in self.positions.values():
            if pos.name == name:
                raise ValueError("Посада з такою назвою вже існує!")
        pos = Position(name, access_level, salary)
        self.positions[pos.id] = pos
        print(f"Посаду '{name}' додано. ID: {pos.id}")
        self.save_data()

    def add_employee(self, first_name: str, last_name: str, position_id: str, hire_date: datetime.date) -> None:
        if position_id not in self.positions:
            raise ValueError("Такої посади немає. Спочатку додайте посаду!")
        position = self.positions[position_id]
        emp = Employee(first_name, last_name, position, hire_date)
        self.employees.append(emp)
        print(f"Співробітника {first_name} {last_name} додано. ID: {emp.id}")
        self.save_data()

    def list_employees(self, sort_by: str = "last_name"):
        if sort_by == "last_name":
            sorted_emps = sorted(self.employees, key=lambda e: e.last_name)
        elif sort_by == "position":
            sorted_emps = sorted(self.employees, key=lambda e: e.position.name)
        elif sort_by == "hire_date":
            sorted_emps = sorted(self.employees, key=lambda e: e.hire_date)
        else:
            sorted_emps = self.employees

        print("\n--- Список співробітників ---")
        for emp in sorted_emps:
            print(emp)

    def delete_employee(self, employee_id: str) -> None:
        """Видаляє співробітника за його унікальним ID."""
        for emp in self.employees:
            if emp.id == employee_id:
                self.employees.remove(emp)
                print(f"Співробітника з ID {employee_id} видалено.")
                self.save_data()
                return
        print("Співробітника з таким ID не знайдено.")

    def update_employee(self, employee_id: str, **kwargs) -> None:
        """
        Оновлює дані співробітника, знайденого за його ID.
        Підтримувані ключі:
          - new_first_name: нове ім'я;
          - new_last_name: нове прізвище;
          - new_position: новий ID посади;
          - new_hire_date: нова дата прийняття (як datetime.date).
        """
        for emp in self.employees:
            if emp.id == employee_id:
                if "new_first_name" in kwargs and kwargs["new_first_name"]:
                    if Employee.validate_name(kwargs["new_first_name"]):
                        emp.first_name = kwargs["new_first_name"]
                    else:
                        print("Невірний формат нового імені.")
                if "new_last_name" in kwargs and kwargs["new_last_name"]:
                    if Employee.validate_name(kwargs["new_last_name"]):
                        emp.last_name = kwargs["new_last_name"]
                    else:
                        print("Невірний формат нового прізвища.")
                if "new_position" in kwargs and kwargs["new_position"]:
                    new_pos_id = kwargs["new_position"]
                    if new_pos_id in self.positions:
                        emp.position = self.positions[new_pos_id]
                    else:
                        print("Вказана посада не знайдена.")
                if "new_hire_date" in kwargs and kwargs["new_hire_date"]:
                    new_date = kwargs["new_hire_date"]
                    if new_date <= datetime.date.today():
                        emp.hire_date = new_date
                    else:
                        print("Дата не може бути в майбутньому.")
                print("Інформацію оновлено.")
                self.save_data()
                return
        print("Співробітника з таким ID не знайдено.")

    def display_payroll_info(self):
        Payroll.display_payroll(self.employees)
        total = sum(emp.position.salary for emp in self.employees)
        print(f"\nЗагальна сума зарплат (брутто): {total}")


# Функція для зчитування дати у форматі YYYY-MM-DD
def input_date(prompt: str) -> datetime.date:
    while True:
        date_str = input(prompt)
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Невірний формат дати. Будь ласка, використовуйте формат YYYY-MM-DD.")


# Головна функція з інтерактивним меню
def main():
    manager = PersonnelManager()

    while True:
        print("\n=== Меню управління персоналом ===")
        print("1. Додати посаду")
        print("2. Додати співробітника")
        print("3. Показати список співробітників")
        print("4. Оновити дані співробітника (за ID)")
        print("5. Видалити співробітника (за ID)")
        print("6. Показати зарплатну відомість")
        print("7. Вийти")
        choice = input("Ваш вибір (1-7): ")

        if choice == "1":
            try:
                name = input("Назва посади: ")
                access_level = int(input("Рівень доступу (1-5): "))
                salary = float(input("Зарплата: "))
                manager.add_position(name, access_level, salary)
            except ValueError as e:
                print("Помилка:", e)

        elif choice == "2":
            try:
                first_name = input("Ім'я співробітника: ")
                last_name = input("Прізвище співробітника: ")
                print("Доступні посади:")
                for pos in manager.positions.values():
                    print(pos)
                position_id = input("Введіть ID посади: ")
                hire_date = input_date("Дата прийняття на роботу (YYYY-MM-DD): ")
                manager.add_employee(first_name, last_name, position_id, hire_date)
            except ValueError as e:
                print("Помилка:", e)

        elif choice == "3":
            print("Сортувати за:")
            print("1. Прізвище")
            print("2. Посада")
            print("3. Дата прийняття")
            sort_choice = input("Ваш вибір (1-3): ")
            if sort_choice == "1":
                manager.list_employees("last_name")
            elif sort_choice == "2":
                manager.list_employees("position")
            elif sort_choice == "3":
                manager.list_employees("hire_date")
            else:
                manager.list_employees()

        elif choice == "4":
            print("Поточні співробітники:")
            manager.list_employees()
            emp_id = input("Введіть ID співробітника для оновлення: ")
            print("Введіть нові дані (залиште поле порожнім, якщо не потрібно змінювати):")
            new_first_name = input("Нове ім'я: ")
            new_last_name = input("Нове прізвище: ")
            print("Доступні посади:")
            for pos in manager.positions.values():
                print(pos)
            new_position = input("Введіть новий ID посади: ")
            new_date_str = input("Нова дата прийняття (YYYY-MM-DD): ")
            kwargs = {}
            if new_first_name:
                kwargs["new_first_name"] = new_first_name
            if new_last_name:
                kwargs["new_last_name"] = new_last_name
            if new_position:
                kwargs["new_position"] = new_position
            if new_date_str:
                try:
                    new_date = datetime.datetime.strptime(new_date_str, "%Y-%m-%d").date()
                    kwargs["new_hire_date"] = new_date
                except ValueError:
                    print("Невірний формат дати. Оновлення дати пропущено.")
            manager.update_employee(emp_id, **kwargs)

        elif choice == "5":
            print("Поточні співробітники:")
            manager.list_employees()
            emp_id = input("Введіть ID співробітника для видалення: ")
            manager.delete_employee(emp_id)

        elif choice == "6":
            manager.display_payroll_info()

        elif choice == "7":
            print("Вихід з програми.")
            break

        else:
            print("Невірний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()
