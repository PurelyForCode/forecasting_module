from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProphetModel:
    id: str
    product_id: str
    model_path: str
    trained_at: datetime
    version: int

