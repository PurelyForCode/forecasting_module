from datetime import date
from typing import Literal, TypedDict
import numpy as np
import pandas as pd
from fastapi import HTTPException
from prophet import Prophet
from statsforecast import StatsForecast
from statsforecast.models import CrostonClassic, CrostonOptimized, CrostonSBA


class ForecastOneInput(TypedDict):
    product_id: str
    account_id: str
    data_start_date: date
    data_end_date: date
    forecast_start_date: date
    forecast_end_date: date
    forecasting_method: Literal["prophet", "croston"]


class ForecastAllInput(TypedDict):
    account_id: str
    data_start_date: date
    data_end_date: date
    forecast_start_date: date
    forecast_end_date: date


class ForecastManager:
    def prophet_forecast(
        self,
        sales: pd.DataFrame,
        forecast_start_date: date,
        forecast_end_date: date,
        model: Prophet | None = None
    ) -> pd.DataFrame:
        """
        Generate a Prophet forecast between forecast_start_date and forecast_end_date.

        Args:
            sales (pd.DataFrame): Historical daily sales data.
                Must contain:
                  - 'ds': datetime column
                  - 'y': numeric sales quantity
            forecast_start_date (date): First day to include in output.
            forecast_end_date (date): Last day to include in output.
            model (Prophet | None): Optional pre-trained model.

        Returns:
            pd.DataFrame: Prophet forecast including ['ds', 'yhat', 'yhat_lower', 'yhat_upper'].
        """
        if sales.empty:
            raise HTTPException(409, {"message": "Sales data is empty — cannot forecast."})

        if not {"ds", "y"}.issubset(sales.columns):
            raise HTTPException(409, {"message": "Sales DataFrame must contain columns ['ds', 'y']."})

        df = sales.sort_values("ds").copy()
        df["ds"] = pd.to_datetime(df["ds"])

        # Fit model
        if model is None:
            model = Prophet()
            model.fit(df)

        last_date = df["ds"].max().date()
        days_to_forecast = (forecast_end_date - last_date).days

        if days_to_forecast <= 0:
            raise HTTPException(
                409,
                {"message": f"Forecast end date ({forecast_end_date}) must be after last sale date ({last_date})."}
            )

        # Generate future dataframe
        future = model.make_future_dataframe(
            periods=days_to_forecast,
            freq="D",
            include_history=False
        )

        forecast: pd.DataFrame = model.predict(future)
        forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]] # pyright: ignore


        # --- Filter forecast window ---
        forecast["ds"] = pd.to_datetime(forecast["ds"])
        ds_series: pd.Series = forecast["ds"]  # pyright: ignore
        mask = (ds_series.dt.date >= forecast_start_date) & (ds_series.dt.date <= forecast_end_date)
        forecast = forecast.loc[mask].reset_index(drop=True)

        if forecast.empty:
            raise HTTPException(
                409,
                {"message": "No forecast data falls within the specified date range."}
            )

        return forecast



    def croston_forecast(
        self,
        data: pd.DataFrame,
        forecast_start_date: date,
        forecast_end_date: date,
    ) -> pd.DataFrame:
        # Ensure proper columns
        if not {"ds", "y"}.issubset(data.columns):
            raise ValueError("Data must contain 'ds' (date) and 'y' (value) columns.")

        # Add unique_id for StatsForecast
        data["unique_id"] = "product_1"
        data["ds"] = pd.to_datetime(data["ds"])
        data = data.sort_values("ds")

        # --- Initialize model ---
        sf = StatsForecast(models=[CrostonOptimized()], freq="D")

        # --- Calculate forecast horizon (h) ---
        last_date = data["ds"].max().date()
        h = (forecast_end_date - last_date).days

        if h <= 0:
            raise ValueError("forecast_end_date must be after the last date in your data.")

        # --- Forecast ---
        forecasts = sf.forecast(df=data, h=h).reset_index() # pyright: ignore

        # --- Filter to your desired forecast window ---
        forecasts["ds"] = pd.to_datetime(forecasts["ds"])
        mask = (forecasts["ds"].dt.date >= forecast_start_date) & (forecasts["ds"].dt.date <= forecast_end_date)
        forecasts = forecasts.loc[mask]

        print(forecasts)
        return forecasts

