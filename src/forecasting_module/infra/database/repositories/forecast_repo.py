from psycopg2.extensions import cursor
from uuid_utils import UUID
from forecasting_module.domain.entities.forecast import Forecast
from typing import Optional, Tuple, Any


class ForecastRepository:
    def __init__(self, cur: cursor):
        self.cur = cur

    def create_forecast(self, forecast: Forecast):
        sql = """
        INSERT INTO forecast ( 
            id,
            product_id,
            account_id,
            data_start_date,
            data_end_date,
            forecast_start_date,
            forecast_end_date,
            processed,
            created_at,
            updated_at,
            deleted_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        self.cur.execute(
            sql,
            (
                forecast.id,
                forecast.product_id,
                forecast.account_id,
                forecast.data_start_date,
                forecast.data_end_date,
                forecast.forecast_start_date,
                forecast.forecast_end_date,
                False,
                forecast.created_at,
                forecast.updated_at,
                forecast.deleted_at,
            ),
        )

    def get_forecast(self, sales_forecast_id: UUID) -> Optional[Forecast]:
        sql = """
        SELECT  
            id,
            product_id,
            account_id,
            data_start_date,
            data_end_date,
            forecast_start_date,
            forecast_end_date,
            created_at,
            updated_at,
        from forecast
        WHERE 
            id = %s
        AND deleted_at IS NULL"""
        self.cur.execute(sql, str(sales_forecast_id))
        row: Optional[Tuple[Any, ...]] = self.cur.fetchone()
        if row is None:
            return None
        forecast = Forecast(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], None
        )
        return forecast
