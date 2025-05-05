import datetime
import uuid
from typing import Dict, Optional
from position import Position


class Employee:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        position: Position,
        hire_date: datetime.date,
        id: Optional[str] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.hire_date = hire_date

        # Валідація імені та прізвища
        if not self.validate_name(self.first_name):
            raise ValueError(
                "Ім'я має містити лише літери та починатися з великої літери."
            )
        if not self.validate_name(self.last_name):
            raise ValueError(
                "Прізвище має містити лише літери та починатися з великої літери."
            )
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
        cls, data: Dict, positions: Dict[str, Position]
    ) -> Optional["Employee"]:
        # парсимо дату
        try:
            hd = datetime.datetime.strptime(
                data.get("hire_date", ""), "%Y-%m-%d"
            ).date()
        except Exception:
            print(
                f"Некоректна дата для співробітника {data.get('first_name', '?')} {data.get('last_name', '?')}"
            )
            return None
        # шукаємо об’єкт Position
        pos = positions.get(data.get("position_id"))
        if not pos:
            print(
                f"Посада з ID {data.get('position_id')} не знайдена для {data.get('first_name')} {data.get('last_name')}"
            )
            return None
        return cls(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            position=pos,
            hire_date=hd,
            id=data.get("id"),
        )

    def __str__(self) -> str:
        return (
            f"{self.first_name} {self.last_name} (ID: {self.id}) | "
            f"{self.position.name} | Прийнятий: {self.hire_date.isoformat()}"
        )
