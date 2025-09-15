from datetime import date, datetime

from src.app.repositories.forecast_entry_repository import ForecastEntryRepository
from src.app.repositories.product_setting_repository import ProductSettingRepository
from src.app.repositories.sale_repository import SaleRepository
from src.app.services.forecast_service import ForecastService
from src.app.repositories.forecast_repository import ForecastRepository
from src.app.models.forecast import Forecast
from dataclasses import dataclass
from uuid import uuid4,UUID

class NotEnoughSalesException(Exception):
    def __init__(self, message="Not enough sales to continue."):
        super().__init__(message)

class ProductSettingMissingError(Exception):
    def __init__(self, setting_name=None):
        message = f"Missing required product setting: {setting_name}" if setting_name else "A required product setting is missing."
        super().__init__(message)

@dataclass
class GenerateSingleForecastInput:
    account_id: UUID
    product_id: UUID
    forecast_start_date: date
    forecast_end_date: date
    data_start_date: date
    data_end_date: date

class GenerateSingleForecast:
    def __init__(
        self,
        forecast_repo: ForecastRepository,
        forecast_entry_repo: ForecastEntryRepository,
        sale_repo: SaleRepository,
        setting_repo:ProductSettingRepository,
        forecast_service: ForecastService
    ):
        self.forecast_repo = forecast_repo
        self.forecast_entry_repo = forecast_entry_repo
        self.forecast_service = forecast_service
        self.sale_repo = sale_repo
        self.setting_repo = setting_repo

    def handle(self, params:GenerateSingleForecastInput):
        now = datetime.now()
        id = uuid4()
        forecast = Forecast(id, params.product_id, params.account_id, params.data_start_date, params.data_end_date, params.forecast_start_date, params.forecast_end_date, now, now, None)
        #Save forecast to db
        self.forecast_repo.create_forecast(forecast)
        sales = self.sale_repo.find_by_product_id(params.product_id)
        if len(sales):
            raise NotEnoughSalesException()
        setting = self.setting_repo.find_by_product_id(params.product_id)
        if setting is None:
            raise ProductSettingMissingError()
        dataframe = self.forecast_service.generate_individual_forecast(params.forecast_start_date, params.forecast_end_date, sales, setting)
        return dataframe