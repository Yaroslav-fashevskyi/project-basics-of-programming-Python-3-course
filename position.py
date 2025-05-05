import uuid
from typing import Dict, Optional


class Position:
    """
    Представляє посаду в компанії.

    Атрибути:
        id (str): Унікальний ідентифікатор посади.
        name (str): Назва посади.
        access_level (int): Рівень доступу (1–5).
        salary (float): Грошова ставка для цієї посади.
    """

    ALLOWED_ACCESS_LEVELS = [1, 2, 3, 4, 5]

    def __init__(
        self,
        name: str,
        access_level: int = 1,
        salary: float = 0.0,
        id: Optional[str] = None,
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
            raise ValueError(
                f"Рівень доступу має бути одним із {Position.ALLOWED_ACCESS_LEVELS}."
            )

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
            id=data.get("id"),
        )

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id}) – Рівень {self.access_level}, Зарплата {self.salary:.2f}"
