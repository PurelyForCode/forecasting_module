from fastapi import APIRouter
from pydantic import BaseModel
from psycopg2.extensions import connection
from starlette.responses import JSONResponse

from src.app.config.db_config import pg_pool
from src.app.repositories.forecast_entry_repository import ForecastEntryRepository
from src.app.repositories.product_setting_repository import ProductSettingRepository
from src.app.repositories.sale_repository import SaleRepository
from src.app.repositories.product_repository import ProductRepository
from src.app.repositories.forecast_repository import ForecastRepository
from src.app.services.forecast_service import ForecastService
from src.app.usecases.generate_single_forecast.usecase import GenerateSingleForecast, GenerateSingleForecastInput
from datetime import date
from uuid_utils import UUID

forecast_router = APIRouter()


class ForecastRequest(BaseModel):
    accountId: str
    forecastStartDate: date
    forecastEndDate: date
    dataStartDate: date
    dataEndDate: date

@forecast_router.post("/forecasts/{product_id}")
def forecast(product_id: str, request: ForecastRequest):
    conn:connection = pg_pool.getconn()
    cur = conn.cursor()
    sale_repository = SaleRepository(cur)
    setting_repository = ProductSettingRepository(cur)
    forecast_repository = ForecastRepository(cur)
    forecast_entry_repository = ForecastEntryRepository(cur)
    forecast_service = ForecastService()
    usecase = GenerateSingleForecast(
        forecast_repository,
        forecast_entry_repository,
        sale_repository,
        setting_repository,
        forecast_service
    )
    input = GenerateSingleForecastInput(
        request.accountId,
        request.productId,
        request.forecastStartDate,
        request.forecastEndDate,
        request.dataStartDate,
        request.dataEndDate
    )
    usecase.handle(input)

    return JSONResponse(
        status_code=200,
        content={"message": "Forecast generated successfully"}
    )


@forecast_router.post("/forecasts")
def forecast(product_id: str, request: ForecastRequest):
    conn:connection = pg_pool.getconn()
    cur = conn.cursor()
    sale_repository = SaleRepository(cur)
    product_setting_repository = ProductSettingRepository(cur)
    forecast_entry_repository = ForecastEntryRepository(cur)
    product_repository = ProductRepository(cur)
    forecast_service = ForecastService(sale_repository, product_setting_repository, forecast_entry_repository, product_repository)
    forecast_service.generate_all_forecast(request.forecastStartDate, request.forecastEndDate, request.historicalDaysCount)

    return JSONResponse(
        status_code=200,
        content={"message": "Forecast generated successfully"}
    )
