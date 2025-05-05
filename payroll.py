from typing import List, Dict
from employee import Employee


class Payroll:
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
