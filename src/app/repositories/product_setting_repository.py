from psycopg2.extensions import cursor
from uuid_utils import UUID
from src.app.models.product_setting import ProductSetting

class ProductSettingRepository:
    def __init__(self, cur: cursor):
        self.cur = cur

    def find_by_product_id(self, product_id: UUID):
        sql = """
            SELECT
                id,
                product_id,
                classification,
            FROM product_setting
            WHERE 
                product_id = %s 
        """
        self.cur.execute(sql, (str(product_id),))
        row = self.cur.fetchone()
        if row is None:
            return None
        return ProductSetting(row[0],row[1],row[2])