import uuid
from typing import Any
import pandas as pd
from psycopg2.extensions import cursor
from uuid_utils import uuid7, UUID

class ForecastEntryRepository:
    def __init__(self, cur: cursor):
        self.cur = cur

    def save_forecast(self, sales_forecast_id: UUID, forecast_df: pd.DataFrame):
        rows = []
        for _, row in forecast_df.iterrows():
            rows.append((
                str(uuid7()),             # id
                str(sales_forecast_id),       # sales_forecast_id
                float(row["yhat"]),           # prediction
                float(row["yhat_upper"]),     # upper bound
                float(row["yhat_lower"]),     # lower bound
                row["ds"].date()              # date (ensure DATE type)
            ))

        insert_query = """
            INSERT INTO sales_forecast_entry (
                id, sales_forecast_id, yhat, yhat_upper, yhat_lower, date
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cur.executemany(insert_query, rows)
