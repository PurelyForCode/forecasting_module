from typing import TypedDict, Literal
from datetime import date
from forecasting_module.infra.database.repositories.forecast_repo import (
    ForecastRepository,
)


class GenerateSingleForecastInput(TypedDict):
    product_id: str
    account_id: str
    data_start_date: date
    data_end_date: date
    forecast_start_date: date
    forecast_end_date: date
    forecasting_method: Literal["prophet", "croston"]


class GenerateSingleForecastUsecase:

    forecast_repo: forecast_repo

    def __init__(
        self,
    ) -> None:
        pass

    def generate_single_forecast(input: GenerateSingleForecastInput):
        print("ok")
        pass
