from pydantic import BaseModel, Field
from  typing import Literal
from datetime import date
# from uuid_utils import UUID


class GenerateSingleForecastBody(BaseModel):
    account_id: str = Field(alias="accountId")
    data_start_date: date = Field(alias="dataStartDate")
    data_end_date: date = Field(alias="dataEndDate")
    forecast_start_date: date = Field(alias="forecastStartDate")
    forecast_end_date: date = Field(alias="forecastEndDate")
    forecasting_method: Literal["prophet", "croston"] = Field(alias="forecastingMethod")

    class Config:
        populate_by_name = True
