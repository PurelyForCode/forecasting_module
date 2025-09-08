from datetime import date,datetime
from dataclasses import dataclass
from src.app.models.forecast import Forecast
from uuid_utils import uuid7, UUID

from src.app.repositories.forecast_repository import ForecastRepository


@dataclass
class GenerateAllForecastInput:
    product_id: UUID
    account_id: UUID
    forecast_start_date: date
    forecast_end_date: date
    data_start_date: date
    data_end_date: date


class GenerateAllForecast:
    def __init__(self, forecast_repo: ForecastRepository):
        self.forecast_repo = forecast_repo
    def handle(self, params: GenerateAllForecastInput):
        now = datetime.today()
        forecast = Forecast(
            uuid7(),
            params.product_id,
            params.account_id,
            params.data_start_date,
            params.data_end_date,
            params.forecast_start_date,
            params.forecast_end_date,
            now,
            now,
            None
        )
        self.forecast_repo.create_forecast(forecast)
        #get sales, get settings, based on settings do fast or slow

