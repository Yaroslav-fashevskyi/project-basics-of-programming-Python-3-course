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
        print("4. Повернутися в головне меню")
        choice = input("Вибір: ").strip()

        if choice == "1":
            name = input("Назва посади: ").strip()
            access = int(input("Рівень доступу (1–5): ").strip())
            salary = float(input("Зарплата: ").strip())
            try:
                mgr.add_position(name, access, salary)
                print("Посада додана.")
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
                print("Посаду видалено.")
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "4":
            break

        else:
            print("Невірний вибір, спробуйте ще раз.")


def employees_menu(mgr: PersonnelManager) -> None:
    while True:
        print("=== Управління співробітниками ===")
        print("1. Додати співробітника")
        print("2. Показати всіх співробітників")
        print("3. Видалити співробітника")
        print("4. Повернутися в головне меню")
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
                print("Співробітника додано.")
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "2":
            # просто показати всіх співробітників у порядку додавання
            if not mgr.employees:
                print("Список співробітників порожній.")
            else:
                print("\nСписок усіх співробітників:")
                for e in mgr.employees:
                    print(e)

        elif choice == "3":
            eid = input("ID співробітника для видалення: ").strip()
            try:
                mgr.delete_employee(eid)
                print("Співробітника видалено.")
            except ValueError as e:
                print(f"Помилка: {e}")

        elif choice == "4":
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
            # 1) вибір поля для пошуку
            print(
                """
Оберіть, за чим шукати:
1 – Ім'я
2 – Прізвище
3 – Посада
4 – Дата прийняття на роботу
            """
            )
            field_sel = input("Вибір: ").strip()
            if field_sel not in {"1", "2", "3", "4"}:
                print("Невірний вибір, повертаємось у меню.")
                continue

            # 2) отримуємо сам запит
            if field_sel == "4":
                # для дати використовуємо input_date
                date_query = input_date("Введіть дату прийняття (YYYY-MM-DD): ")
                found = [e for e in mgr.employees if e.hire_date == date_query]
            else:
                prompts = {
                    "1": "Введіть ім'я для пошуку: ",
                    "2": "Введіть прізвище для пошуку: ",
                    "3": "Введіть назву посади для пошуку: ",
                }
                query = input(prompts[field_sel]).strip()
                if not query:
                    print("Пошук відмінено.")
                    continue

                if field_sel == "1":
                    found = [
                        e
                        for e in mgr.employees
                        if query.lower() in e.first_name.lower()
                    ]
                elif field_sel == "2":
                    found = [
                        e for e in mgr.employees if query.lower() in e.last_name.lower()
                    ]
                else:  # поле 3 – посада
                    found = [
                        e
                        for e in mgr.employees
                        if query.lower() in e.position.name.lower()
                    ]

            # 3) вивід результатів
            if not found:
                print("Нічого не знайдено за запитом.")
            else:
                print(f"\nЗнайдено {len(found)} співробітників:")
                for emp in found:
                    print(emp)

        elif choice == "4":
            mgr.payroll_info()

        elif choice == "5":
            print("Завершення роботи.")
            sys.exit(0)

        else:
            print("Невірний вибір, спробуйте ще раз.")


if __name__ == "__main__":
    main()
