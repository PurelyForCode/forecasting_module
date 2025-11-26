from typing import Literal
from dataclasses import dataclass

@dataclass
class ProductSetting:
    id: str
    product_id: str
    classification: Literal["slow", "fast"]

