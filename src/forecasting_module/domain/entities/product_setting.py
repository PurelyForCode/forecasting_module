from typing import Literal

class ProductSetting:
    classification: Literal["slow", "fast"]

    def __init__(self, id: str, product_id: str, classification: Literal["slow", "fast"], ):
        self.id = id
        self.product_id = product_id
        self.classification = classification