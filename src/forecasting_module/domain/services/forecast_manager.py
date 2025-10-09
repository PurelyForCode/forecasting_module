from datetime import date
from typing import Literal, TypedDict
import numpy as np
from fastapi import HTTPException
from forecasting_module.domain.entities.sale import Sale
import pandas as pd
from prophet import Prophet


class ForecastOneInput(TypedDict):
    product_id: str
    account_id: str
    data_start_date: date
    data_end_date: date
    forecast_end_date: date
    forecasting_method: Literal["prophet", "croston"]


class ForecastAllInput(TypedDict):
    account_id: str
    data_start_date: date
    data_end_date: date
    forecast_end_date: date


class ForecastManager:
    def prophet_forecast(
        self,
        sales: list[Sale],
        forecast_end_date: date,
        model: Prophet | None = None
    ) -> pd.DataFrame:
        """
        Generate a Prophet forecast up to a specified end date using Prophet's
        built-in make_future_dataframe() for future dates.

        Args:
            sales (list[Sale]): Historical sales data.
            forecast_end_date (date): Date to forecast up to (inclusive).
            model (Prophet | None): Optional pre-trained model.

        Returns:
            pd.DataFrame: Prophet forecast dataframe (includes both actual + forecast).
        """
        if not sales:
            raise HTTPException(409, {"message":"Sales data is empty — cannot forecast."})

        df = pd.DataFrame([{"ds": s.date, "y": s.quantity} for s in sales]).sort_values("ds")

        if model is None:
            model = Prophet()
            model.fit(df)

        last_date = df["ds"].max()
        days_to_forecast = (forecast_end_date - last_date).days

        if days_to_forecast <= 0:
            raise HTTPException(
                409, 
                {
                    "message": f"Forecast end date ({forecast_end_date}) must be after last sale date ({last_date})."
                }
            )
        future = model.make_future_dataframe(periods=days_to_forecast, freq="D", include_history=False)
        forecast = model.predict(future)

        return forecast

    def croston_forecast(
            self,
            sales: list[Sale],
            forecast_end_date: date,
            alpha: float = 0.1
        ) -> pd.DataFrame:
            """
            Forecast using Croston’s method for intermittent demand.

            Args:
                sales (list[Sale]): Historical sales data (date + quantity).
                forecast_end_date (date): Date up to which to forecast.
                alpha (float): Smoothing parameter (default=0.1).

            Returns:
                pd.DataFrame: DataFrame with columns ['ds', 'forecast'].
            """
            if not sales:
                raise HTTPException(409, {"message": "Sales data is empty — cannot forecast."})

            df = pd.DataFrame([{"ds": s.date, "y": s.quantity} for s in sales]).sort_values("ds")
            df = df.set_index("ds")
            full_idx = pd.date_range(df.index.min(), df.index.max(), freq="D")
            df = df.reindex(full_idx, fill_value=0)
            df.index.name = "ds"

            # --- Croston’s algorithm ---
            y = df["y"].values
            # n = len(y)

            demand = []
            intervals = []
            last_demand = 0
            last_interval = 1
            t = 1

            for val in y:
                if val > 0:
                    if last_demand == 0:
                        z = val
                        p = t
                    else:
                        z = (1 - alpha) * last_demand + alpha * val
                        p = (1 - alpha) * last_interval + alpha * t
                    last_demand, last_interval = z, p
                    t = 1
                else:
                    t += 1
                demand.append(last_demand)
                intervals.append(last_interval)

            df["z_t"] = demand
            df["p_t"] = intervals
            df["forecast"] = df["z_t"] / df["p_t"]
            last_date = df.index.max() #type: ignore
            days_to_forecast = (forecast_end_date - last_date.date()).days # type: ignore
            if days_to_forecast <= 0:
                raise HTTPException(
                    409,
                    {
                        "message": f"Forecast end date ({forecast_end_date}) must be after last sale date ({last_date.date()})." #type: ignore
                    }
                )

            future_idx = pd.date_range(start=last_date + pd.Timedelta(days=1), end=forecast_end_date, freq="D")#type: ignore
            future_forecast = np.full(len(future_idx), df["forecast"].iloc[-1])  #type: ignore

            forecast_df = pd.DataFrame({
                "ds": future_idx,
                "forecast": future_forecast
            })

            return forecast_df
