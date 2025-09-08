from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID


@dataclass
class Forecast:
    id: UUID
    product_id: UUID
    account_id: UUID
    data_start_date: date
    data_end_date: date
    forecast_start_date: date
    forecast_end_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
