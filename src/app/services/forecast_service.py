from datetime import date

from pandas import DataFrame
from prophet import Prophet
import pandas as pd
from uuid_utils import UUID
from datetime import timedelta
from src.app.models.sale import Sale


from src.app.repositories.forecast_entry_repository import ForecastEntryRepository
from src.app.repositories.product_setting_repository import ProductSettingRepository
from src.app.repositories.sale_repository import SaleRepository
from src.app.repositories.product_repository import ProductRepository
from src.app.repositories.forecast_repository import ForecastRepository
from src.app.models.product_setting import ProductSetting


class ForecastService:

    def _fast_product_forecast(self, sales: list[Sale], start_date: date, end_date: date):
        df = pd.DataFrame([{"ds": s.date, "y": s.quantity} for s in sales])
        m = Prophet()
        m.fit(df)
        future = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D"
        )
        future_df = pd.DataFrame({"ds": future})
        forecast = m.predict(future_df)
        return forecast

    def _slow_product_forecast(self)-> DataFrame:
        raise Exception("not implemented yet")

    def generate_individual_forecast(
            self,
            start_date: date,
            end_date: date,
            sales: list[Sale],
            setting: ProductSetting,
    )-> DataFrame:
        if setting.classification == "slow":
            forecast = self._slow_product_forecast()
            return forecast
        elif setting.classification == "fast":
            forecast = self._fast_product_forecast(sales, start_date, end_date)
            return forecast


    def generate_all_forecast(
            self,
            sale_forecast_id: UUID,
            forecast_start_date: date,
            forecast_end_date: date,
            historical_days_count: int
    ):
        product_ids = self.product_repository.find_all_product_id()
        cutoff_date = date.today() - timedelta(days=historical_days_count)
        for id in product_ids:
            product_setting = self.product_setting_repository.find_by_product_id(id)
            sales = self.sale_repository.find_by_product_id(id, cutoff_date)
            if product_setting.classification == "slow":
                self._slow_product_forecast()
            elif product_setting.classification == "fast":
                self._fast_product_forecast(sale_forecast_id, sales, forecast_start_date, forecast_end_date)
