from datetime import date
from psycopg.cursor import Cursor
from forecasting_module.domain.entities.sale import Sale

class SaleRepository:
    def __init__(self, cur: Cursor):
        self.cur = cur

    def get_date_bounds(self, product_id: str) -> tuple[date, date] | None:
        sql = """
            SELECT 
                MIN(date) AS first_date,
                MAX(date) AS last_date
            FROM sale
            WHERE 
                product_id = %s 
                AND deleted_at IS NULL
        """
        self.cur.execute(sql, (product_id,))
        row = self.cur.fetchone()
        return (row[0], row[1]) if row and row[0] and row[1] else None

    def find_by_product_id_and_date_range(
        self, product_id: str, start_date: date, end_date: date
    ) -> list[Sale]:
        sql = """
            SELECT 
                SUM(quantity) AS total_quantity,
                date
            FROM sale
            WHERE 
                product_id = %s
                AND deleted_at IS NULL
                AND date BETWEEN %s AND %s
            GROUP BY product_id, date
            ORDER BY date ASC
        """
        self.cur.execute(sql, (product_id, start_date, end_date))
        rows = self.cur.fetchall()
        return [Sale(row[0], row[1]) for row in rows]



