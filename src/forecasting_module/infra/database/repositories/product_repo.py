from psycopg2.extensions import cursor
from typing import List


class ProductRepository:
    def __init__(self, cur: cursor):
        self.cur = cur

    def get_product_ids(self) -> List[str]:
        self.cur.execute("SELECT id FROM product WHERE deleted_at IS NULL")
        rows = self.cur.fetchall()
        return [row[0] for row in rows]
