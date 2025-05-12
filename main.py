import sys
from personnel_manager import PersonnelManager
from utils import input_date


def print_main_menu() -> None:
    print(
        """
=== Головне меню ===
1. Управління посадами
2. Редагування персоналу
3. Пошук співробітників
4. Зарплата та звіти
5. Вийти
"""
    )


def positions_menu(mgr: PersonnelManager) -> None:
    while True:
        print("=== Управління посадами ===")
        print("1. Додати посаду")
        print("2. Показати всі посади")
        print("3. Видалити посаду")
        print("4. Оновити інформацію про посаду")
        print("5. Повернутися в головне меню")
        choice = input("Вибір: ").strip()

        if choice == "1":
            name = input("Назва посади: ").strip()
            access = int(input("Рівень доступу (1–5): ").strip())
            salary = float(input("Зарплата: ").strip())
            try:
                mgr.add_position(name, access, salary)
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "2":
            print("Список посад:")
            for pos in mgr.positions.values():
                print(pos)

        elif choice == "3":
            pid = input("ID посади для видалення: ").strip()
            try:
                mgr.delete_position(pid)
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "4":
            pid = input("ID посади для оновлення: ").strip()
            print("Що оновити?")
            print("1. Назва")
            print("2. Рівень доступу")
            print("3. Зарплата")
            field = input("Вибір поля: ").strip()
            kwargs = {}
            try:
                if field == "1":
                    kwargs["name"] = input("Нова назва: ").strip()
                elif field == "2":
                    kwargs["access_level"] = int(
                        input("Новий рівень доступу (1–5): ").strip()
                    )
                elif field == "3":
                    kwargs["salary"] = float(input("Нова зарплата: ").strip())
                else:
                    print("Невірний вибір.")
                    continue
                mgr.update_position(pid, **kwargs)
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "5":
            break

        else:
            print("Невірний вибір, спробуйте ще раз.")


def employees_menu(mgr: PersonnelManager) -> None:
    while True:
        print("=== Управління співробітниками ===")
        print("1. Додати співробітника")
        print("2. Показати всіх співробітників")
        print("3. Видалити співробітника")
        print("4. Оновити інформацію про співробітника")
        print("5. Показати співробітників з сортуванням")
        print("6. Повернутися в головне меню")
        choice = input("Вибір: ").strip()

        if choice == "1":
            first = input("Ім'я: ").strip()
            last = input("Прізвище: ").strip()
            print("Доступні посади:")
            for pos in mgr.positions.values():
                print(f"{pos.id} – {pos.name}")
            pid = input("ID посади: ").strip()
            date = input_date("Дата прийняття (YYYY-MM-DD): ")
            try:
                mgr.add_employee(first, last, pid, date)
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "2":
            for e in mgr.employees:
                print(e)

        elif choice == "3":
            eid = input("ID співробітника для видалення: ").strip()
            try:
                mgr.delete_employee(eid)
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "4":
            eid = input("ID співробітника для оновлення: ").strip()
            print("Що оновити?")
            print("1. Ім'я")
            print("2. Прізвище")
            print("3. Посада")
            print("4. Дата прийняття")
            field = input("Вибір поля: ").strip()
            kwargs = {}
            try:
                if field == "1":
                    kwargs["first_name"] = input("Нове ім'я: ").strip()
                elif field == "2":
                    kwargs["last_name"] = input("Нове прізвище: ").strip()
                elif field == "3":
                    print("Доступні посади:")
                    for pos in mgr.positions.values():
                        print(f"{pos.id} – {pos.name}")
                    kwargs["position_id"] = input("Новий ID посади: ").strip()
                elif field == "4":
                    kwargs["hire_date"] = input_date(
                        "Нова дата прийняття (YYYY-MM-DD): "
                    )
                else:
                    print("Невірний вибір поля.")
                    continue

                mgr.update_employee(eid, **kwargs)
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "5":
            print("Сортувати за:")
            print("1. Прізвище")
            print("2. Посада")
            print("3. Дата прийняття")
            sel = input("Вибір: ").strip()
            key_map = {"1": "last_name", "2": "position", "3": "hire_date"}
            sort_by = key_map.get(sel, "last_name")
            for e in mgr.list_employees(sort_by=sort_by):
                print(e)

        elif choice == "6":
            break

        else:
            print("Невірний вибір, спробуйте ще раз.")


def main() -> None:
    mgr = PersonnelManager()

    while True:
        print_main_menu()
        choice = input("Вибір: ").strip()

        if choice == "1":
            positions_menu(mgr)
        elif choice == "2":
            employees_menu(mgr)
        elif choice == "3":
            # Пошук
            print(
                """
Оберіть, за чим шукати:
1 – Ім'я
2 – Прізвище
3 – Посада
4 – Дата прийняття
            """
            )
            field_sel = input("Вибір: ").strip()
            if field_sel not in {"1", "2", "3", "4"}:
                print("Невірний вибір.")
                continue
            if field_sel == "4":
                q = input_date("Дата прийняття (YYYY-MM-DD): ")
                found = [e for e in mgr.employees if e.hire_date == q]
            else:
                prompts = {"1": "ім'я", "2": "прізвище", "3": "посаду"}
                query = input(f"Введіть {prompts[field_sel]}: ").strip().lower()
                if field_sel == "1":
                    found = [e for e in mgr.employees if query in e.first_name.lower()]
                elif field_sel == "2":
                    found = [e for e in mgr.employees if query in e.last_name.lower()]
                else:
                    found = [
                        e for e in mgr.employees if query in e.position.name.lower()
                    ]
            if not found:
                print("Нічого не знайдено.")
            else:
                for e in found:
                    print(e)

        elif choice == "4":
            mgr.payroll_info()

        elif choice == "5":
            print("Вихід.")
            sys.exit(0)

        else:
            print("Невірний вибір.")


if __name__ == "__main__":
    main()
