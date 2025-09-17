from fastapi import APIRouter
from .dto.generate_single_forecast import GenerateSingleForecastBody
from forecasting_module.application.usecases.generate_single_forecast.usecase import (
    generate_single_forecast,
)

forecast_router = APIRouter()


@forecast_router.post("/{product_id}")
async def generate_single_forecast_controller(
    product_id: str, body: GenerateSingleForecastBody
):
    generate_single_forecast(
        {
            "account_id": body.account_id,
            "data_end_date": body.data_end_date,
            "data_start_date": body.data_start_date,
            "forecast_end_date": body.forecast_end_date,
            "forecast_start_date": body.forecast_start_date,
            "forecasting_method": body.forecasting_method,
            "product_id": product_id,
        }
    )
    return {"message": "ok"}
