from dataclasses import dataclass
from uuid_utils import UUID
from datetime import date, datetime
from typing import Optional

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
