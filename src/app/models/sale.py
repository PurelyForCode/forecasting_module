from datetime import datetime, date
from typing import Optional
from uuid import UUID

class Sale:
    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        quantity: int,
        status: str,
        date: date,
    ):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.status = status
        self.date = date

