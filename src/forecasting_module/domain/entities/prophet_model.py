from dataclasses import dataclass
from uuid_utils import UUID
from datetime import datetime

@dataclass
class ProphetModel:
    id: UUID
    product_id: UUID
    model_path: str
    trained_at: datetime
    version: int

