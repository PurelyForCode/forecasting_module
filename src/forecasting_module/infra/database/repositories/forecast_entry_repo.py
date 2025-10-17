import pandas as pd
from psycopg.cursor import Cursor
from typing import List, Tuple
from uuid_utils import uuid7

class ForecastEntryRepository:
    def __init__(self, cur: Cursor):
        self.cur = cur

    def delete_entries_by_forecast_id(self, forecast_id: str) -> None:
        delete_query = """
            DELETE FROM forecast_entry
            WHERE forecast_id = %s
        """
        self.cur.execute(delete_query, (forecast_id,))
        

    def save_forecast_dataframe(self, forecast_id: str, forecast_df: pd.DataFrame) -> None:
        rows: List[Tuple[str, str, float, float, float, str]] = []
        for _, row in forecast_df.iterrows():
            rows.append((
                str(uuid7()),
                str(forecast_id),
                float(row["yhat"]),           
                float(row["yhat_upper"]),     
                float(row["yhat_lower"]),     
                str(row["ds"]),
            ))


        insert_query = """
            INSERT INTO forecast_entry (
                id, forecast_id, yhat, yhat_upper, yhat_lower, date
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cur.executemany(insert_query, rows)
