from psycopg.cursor import Cursor
from forecasting_module.domain.entities.product_setting import ProductSetting

class ProductSettingRepository:
    def __init__(self, cur: Cursor):
        self.cur = cur

    def find_by_product_id(self, product_id: str):
        sql = """
            SELECT
                id,
                product_id,
                classification
            FROM product_setting
            WHERE 
                product_id = %s 
        """
        self.cur.execute(sql, (product_id,))
        row = self.cur.fetchone()
        if row is None:
            return None
        return ProductSetting(row[0], row[1], row[2])
