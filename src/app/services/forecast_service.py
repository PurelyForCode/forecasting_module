from src.app.repositories.forecast_entry_repository import ForecastEntryRepository
from src.app.repositories.product_setting_repository import ProductSettingRepository
from src.app.repositories.sale_repository_repository import SaleRepository
from datetime import date, datetime
from prophet import Prophet
import pandas as pd
from uuid_utils import UUID
from datetime import timedelta


class ForecastService:
    def __init__(self, sale_repository: SaleRepository, product_setting_repository: ProductSettingRepository, forecast_entry_repository: ForecastEntryRepository):
        self.sale_repository = sale_repository
        self.product_setting_repository = product_setting_repository
        self.forecast_entry_repository = forecast_entry_repository

    def generate_forecast(
            self,
            product_id: UUID,
            sale_forecast_id: UUID,
            forecast_start_date: date,
            forecast_end_date: date,
            historical_days_count: int
    ):
        cutoff_date = date.today() - timedelta(days=historical_days_count)
        sales = self.sale_repository.find_by_product_id(product_id, cutoff_date)
        product_setting = self.product_setting_repository.find_by_product_id(product_id)
        if product_setting.classification == "slow":
            raise Exception("not implemented yet")
        elif product_setting.classification == "fast":
            df = pd.DataFrame([{"ds": s.date, "y": s.quantity} for s in sales])
            m = Prophet()
            m.fit(df)
            future = pd.date_range(
                start=forecast_start_date,
                end=forecast_end_date,
                freq="D"
            )
            future_df = pd.DataFrame({"ds": future})
            forecast = m.predict(future_df)
            self.forecast_entry_repository.save_forecast(sale_forecast_id, forecast)

