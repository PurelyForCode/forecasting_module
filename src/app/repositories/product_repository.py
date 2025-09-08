from psycopg2.extensions import cursor
from uuid_utils import UUID

class ProductRepository:
    def __init__(self, cur: cursor):
        self.cur = cur

    def find_all_product_id(self)-> list[UUID]:
        sql = """
            SELECT
                id,
            FROM product
            WHERE 
                deleted_at IS NULL
        """
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        ids = list()
        for row in rows:
            ids.append(UUID(hex=row[0]))
        return ids
