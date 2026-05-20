from dataclasses import dataclass
from datetime import datetime
from typing_extensions import Optional

@dataclass
class ProphetModel:
    id: str
    product_id: str
    name: str
    model_path: str
    active: bool
    trained_at: Optional[datetime ]
