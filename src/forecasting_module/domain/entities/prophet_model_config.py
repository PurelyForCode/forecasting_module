from dataclasses import dataclass
from uuid_utils import UUID

@dataclass
class ProphetModelConfig:
    prophet_model_id: UUID
    pass