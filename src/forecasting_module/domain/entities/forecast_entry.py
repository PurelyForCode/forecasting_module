from dataclasses import dataclass
from uuid_utils import UUID
from datetime import date

@dataclass
class ForecastEntry:
    id: UUID
    forecast_id: UUID
    yhat: float
    yhat_upper: float
    yhat_lower: float
    date: date