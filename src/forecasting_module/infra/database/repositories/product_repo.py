from psycopg.cursor import Cursor
from forecasting_module.domain.entities.product import Product

class ProductRepository:
    def __init__(self, cur: Cursor):
        self.cur = cur

    def find_all(self) -> list[Product]:
        self.cur.execute("SELECT id FROM product WHERE deleted_at IS NULL")
        rows = self.cur.fetchall()
        return [self.to_entity(row) for row in rows]

    def find_one_by_id(self, id: str) -> Product | None:
        self.cur.execute(
            "SELECT id, sale_count FROM product WHERE id = %s AND deleted_at IS NULL", (id,)
        )
        row = self.cur.fetchone()
        return self.to_entity(row) if row else None

    def to_entity(self, row: tuple) -> Product:
        return Product(row[0], row[1])
