from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

class GenerateSingleForecastBody(BaseModel):
    account_id: str = Field(alias="accountId")
    forecast_id: str = Field(alias="forecastId")
    data_depth: int = Field(alias="dataDepth")
    forecast_start_date: date = Field(alias="forecastStartDate")
    forecast_end_date: date = Field(alias="forecastEndDate")
    forecasting_method: Literal["prophet", "croston"] = Field(alias="forecastingMethod")

    class Config:
        populate_by_name = True
