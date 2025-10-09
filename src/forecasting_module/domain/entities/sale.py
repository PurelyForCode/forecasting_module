from dataclasses import dataclass
from datetime import date

@dataclass
class Sale:
    id: str
    product_id: str
    quantity: int
    status: str
    date: date
