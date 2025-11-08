from fastapi import HTTPException, status
from typing import TypedDict, Literal
from datetime import date, timedelta
from forecasting_module.domain.services.forecast_manager import ForecastManager
from forecasting_module.infra.database.repositories.forecast_entry_repo import ForecastEntryRepository
from forecasting_module.infra.database.repositories.forecast_repo import ForecastRepository
from forecasting_module.infra.database.repositories.product_repo import ProductRepository
from forecasting_module.infra.database.repositories.product_setting_repo import ProductSettingRepository
from forecasting_module.infra.database.repositories.sale_repo import SaleRepository
import pandas as pd


class GenerateSingleForecastInput(TypedDict):
    forecast_id: str
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
        product = self.product_repo.find_one_by_id(input["product_id"])
        if not product:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail={"message": "Product not found"})

        bounds = self.sale_repo.get_date_bounds(product.id)
        if not bounds:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "No sales data found"})

        first_date, last_date = bounds
        total_days = (last_date - first_date).days + 1

        # Compute cutoff date based on data_depth percentage
        keep_ratio = input["data_depth"] / 100  # data_depth = 80 means 80%
        cutoff_offset = int(total_days * (1 - keep_ratio))
        cutoff_date = first_date + timedelta(days=cutoff_offset)

        # Fetch only the relevant portion of sales
        sales = self.sale_repo.find_by_product_id_and_date_range(
            product.id, cutoff_date, last_date
        )

        if len(sales) == 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "No sales found in selected range"})

        # Convert to DataFrame for aggregation
        df = pd.DataFrame([{"ds": s.date, "y": s.quantity} for s in sales])

        # Ensure proper datetime type
        df["ds"] = pd.to_datetime(df["ds"])

        # Create a complete daily range between the first and last sales date
        full_range = pd.date_range(df["ds"].min(), df["ds"].max(), freq="D")

        # Reindex to include missing dates and fill with 0s
        df = (
            df.set_index("ds")
              .reindex(full_range, fill_value=0)
              .rename_axis("ds")
              .reset_index()
        )

        if len(df) <= 30:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "Not enough data (min 30 days)"})

        forecast = self.forecast_repo.get_forecast(input["forecast_id"])
        if not forecast:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
                "message": "Internal Server Error",
                "debugMessage": "Forecast was not instantiated"
            })

        # clear previous forecast entries
        self.forecast_entry_repo.delete_entries_by_forecast_id(forecast.id)
        forecast_mgr = ForecastManager()
        if forecast.model_type == "prophet":
            future = forecast_mgr.prophet_forecast(
                model=None, 
                sales=df, 
                forecast_start_date=input["forecast_start_date"],
                forecast_end_date=input["forecast_end_date"]
            )
        else:
            future = forecast_mgr.croston_forecast(df, input["forecast_start_date"], input["forecast_end_date"])
            raise Exception()

        if future is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": "Forecasting failed"})

        self.forecast_entry_repo.save_forecast_dataframe(forecast.id, future)
        return str(forecast.id)
