from fastapi import APIRouter
from forecasting_module.config.pool import pool
from forecasting_module.application.usecases.generate_single_forecast.usecase import GenerateSingleForecastUsecase
from forecasting_module.infra.database.repositories.forecast_entry_repo import ForecastEntryRepository
from forecasting_module.infra.database.repositories.forecast_repo import ForecastRepository
from forecasting_module.infra.database.repositories.product_repo import ProductRepository
from forecasting_module.infra.database.repositories.product_setting_repo import ProductSettingRepository
from forecasting_module.infra.database.repositories.sale_repo import SaleRepository
from forecasting_module.infra.web.forecasts.dto.generate_single_forecast import GenerateSingleForecastBody

forecast_router = APIRouter()


@forecast_router.post("/{product_id}")
async def generate_forecast(
    product_id: str,
    body: GenerateSingleForecastBody
):  
    forecast_id = None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            product_repo = ProductRepository(cur)
            sale_repo = SaleRepository(cur)
            forecast_repo = ForecastRepository(cur)
            forecast_entry_repo = ForecastEntryRepository(cur)
            setting_repo= ProductSettingRepository(cur)
            usecase = GenerateSingleForecastUsecase(
                product_repo, 
                sale_repo, 
                forecast_repo, 
                setting_repo, 
                forecast_entry_repo
            )
            forecast_id = usecase.handle(
                {
                    "account_id": body.account_id, 
                    "forecast_id": body.forecast_id,
                    "data_depth": body.data_depth, 
                    "forecast_end_date": body.forecast_end_date, 
                    "forecast_start_date": body.forecast_start_date, 
                    "forecasting_method": body.forecasting_method, 
                    "product_id": product_id
                }
            )
    return { "data": forecast_id }
