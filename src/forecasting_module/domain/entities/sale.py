from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class Sale:
    id: UUID
    product_id: UUID
    quantity: int
    status: str
    date: date