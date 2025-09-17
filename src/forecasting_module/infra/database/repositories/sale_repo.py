from psycopg2.extensions import cursor
from domain.entities.sale import Sale
from uuid_utils import UUID
from datetime import date
from typing import List


class SaleRepository:
    def __init__(self, cur: cursor):
        self.cur = cur

    def find_by_product_id(self, product_id: UUID, cutoff_date: date) -> list[Sale]:
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
                AND date >= %s
                AND deleted_at IS NULL
        """

        self.cur.execute(sql, (str(product_id), cutoff_date))
        rows = self.cur.fetchall()

        sales: List[Sale] = []
        for row in rows:
            sale = Sale(row[0], row[1], row[2], row[3], row[4])
            sales.append(sale)

        return sales