from dataclasses import dataclass
from datetime import date

@dataclass
class ForecastEntry:
    id: str
    forecast_id: str
    yhat: float
    yhat_upper: float
    yhat_lower: float
    date: date
