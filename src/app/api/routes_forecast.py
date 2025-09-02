from fastapi import APIRouter
from pydantic import BaseModel
from psycopg2.extensions import connection
from starlette.responses import JSONResponse

from src.app.config.db_config import pg_pool
from src.app.repositories.product_setting_repository import ProductSettingRepository
from src.app.repositories.sale_repository_repository import SaleRepository
from src.app.services.forecast_service import ForecastService
from datetime import date

forecast_router = APIRouter()


class ForecastRequest(BaseModel):
    forecastStartDate: date
    forecastEndDate: date
    historicalDaysCount: int


@forecast_router.post("/{product_id}")
def forecast(product_id: str, request: ForecastRequest):
    conn:connection = pg_pool.getconn()
    cur = conn.cursor()
    sale_repository = SaleRepository(cur)
    product_setting_repository = ProductSettingRepository(cur)
    forecast_service = ForecastService(sale_repository, product_setting_repository)
    forecast_service.generate_forecast(product_id, request.forecastStartDate, request.forecastEndDate, request.historicalDaysCount)

    return JSONResponse(
        status_code=200,
        content={"message": "Forecast generated successfully"}
    )