from psycopg.cursor import Cursor
from forecasting_module.domain.entities.sale import Sale


class SaleRepository:
    def __init__(self, cur: Cursor):
        self.cur = cur

    def find_by_product_id(self, product_id: str, limit: int) -> list[Sale]:
        sql = """
            SELECT 
                id, 
                product_id, 
                quantity, 
                status, 
                date 
            FROM sale 
            WHERE 
                product_id = %s 
                AND deleted_at IS NULL
            ORDER BY date DESC
            LIMIT %s
        """
        self.cur.execute(sql, (product_id, limit))
        rows = self.cur.fetchall()

        sales: list[Sale] = [Sale(*row) for row in rows]
        return sales
