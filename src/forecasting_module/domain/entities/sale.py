from dataclasses import dataclass
from datetime import date

@dataclass
class Sale:
    quantity: int
    date: date
