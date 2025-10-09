from fastapi import HTTPException, status
from datetime import datetime
from uuid_utils import uuid7
from typing import TypedDict, Literal
from datetime import date
from forecasting_module.domain.entities.forecast import Forecast
from forecasting_module.domain.services.forecast_manager import ForecastManager
from forecasting_module.infra.database.repositories.forecast_entry_repo import ForecastEntryRepository
from forecasting_module.infra.database.repositories.forecast_repo import ForecastRepository
from forecasting_module.infra.database.repositories.product_repo import ProductRepository
from forecasting_module.infra.database.repositories.product_setting_repo import ProductSettingRepository
from forecasting_module.infra.database.repositories.sale_repo import SaleRepository


class GenerateSingleForecastInput(TypedDict):
    product_id: str
    account_id: str
    data_depth: int
    forecast_start_date: date
    forecast_end_date: date
    forecasting_method: Literal["prophet", "croston"]


class GenerateSingleForecastUsecase:
    def __init__(
        self,
        product_repo: ProductRepository,
        sale_repo: SaleRepository,
        forecast_repo: ForecastRepository,
        setting_repo: ProductSettingRepository,
        forecast_entry_repo: ForecastEntryRepository
    ) -> None:
        self.product_repo = product_repo
        self.sale_repo = sale_repo
        self.forecast_repo = forecast_repo
        self.forecast_entry_repo = forecast_entry_repo
        self.setting_repo = setting_repo

    def handle(self, input: GenerateSingleForecastInput):
        # get product
        product = self.product_repo.find_one_by_id(input["product_id"])
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Product not found"}
            )

        # get sales
        product.sale_count
        limit = round(product.sale_count * input["data_depth"])
        sales = self.sale_repo.find_by_product_id(product.id, limit)
        if len(sales) <= 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Not enough sales data (minimum 30 required)"}
            )

        # get product setting
        setting = self.setting_repo.find_by_product_id(product.id)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Product settings not found"}
            )

        now = datetime.now()

        forecast = Forecast(
            str(uuid7()),
            input["product_id"],
            input["account_id"],
            input["data_depth"],
            input["forecast_start_date"],
            input["forecast_end_date"],
            now,
            now,
            None,
        )

        self.forecast_repo.create_forecast(forecast)

        forecast_mgr = ForecastManager()
        if setting.classification == "fast":
            # Prophet model
            future = forecast_mgr.prophet_forecast(
                model=None,
                sales=sales,
                forecast_end_date=input["forecast_end_date"]
            )
        else:
            # Croston model
            future = forecast_mgr.croston_forecast(
                sales = sales,
                alpha = 0.1,
                forecast_end_date = input["forecast_end_date"]
            )
        if future is None:
            raise HTTPException(500, detail={"message": "Internal Server Error"})

        self.forecast_entry_repo.save_forecast_dataframe(forecast.id, future)

        return {
            "message": "Forecast generated successfully",
            "forecast_id": str(forecast.id)
        }
