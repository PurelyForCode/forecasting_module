from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

@dataclass
class Forecast:
    id: str
    product_id: str
    account_id: str
    prophet_model_id: str | None
    croston_model_id: str | None
    model_type: Literal["croston", "prophet"]
    data_depth: int
    forecast_start_date: date
    forecast_end_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
