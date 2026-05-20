from psycopg.cursor import Cursor
from forecasting_module.domain.entities.prophet_model import ProphetModel
from datetime import date
from dataclasses import dataclass
from datetime import date
from typing import Optional, Literal
from prophet import Prophet
from uuid_utils import uuid7
import pandas as pd


GrowthType = Literal["linear", "logistic", "flat"]
SeasonalityMode = Literal["additive", "multiplicative"]
SeasonalityBool = Literal["auto", "true", "false"]

@dataclass
class ProphetSeasonality:
    id: str
    model_setting_id: str

    name: str
    period: float
    fourier_order: int

    prior_scale: Optional[float]
    mode: Optional[SeasonalityMode]


@dataclass
class ProphetChangepoint:
    id: str
    model_setting_id: str
    ds: date


@dataclass
class ProphetModelSetting:
    id: str
    prophet_model_id: str

    growth: GrowthType

    changepoint_range: Optional[float]
    changepoint_prior_scale: Optional[float]

    yearly_seasonality: Optional[SeasonalityBool]
    weekly_seasonality: Optional[SeasonalityBool]
    daily_seasonality: Optional[SeasonalityBool]

    seasonality_mode: Optional[SeasonalityMode]
    seasonality_prior_scale: Optional[float]
    holidays_prior_scale: Optional[float]

    interval_width: float
    uncertainty_samples: int

    scaling: Optional[str]
    holidays_mode: Optional[str]

    seasons: list[ProphetSeasonality]
    changepoints: list[ProphetChangepoint]

def build_default_prophet_settings(prophet_model_id: str, model: Prophet) -> ProphetModelSetting:
    return ProphetModelSetting(
        id=str(uuid7()),
        prophet_model_id=prophet_model_id,

        growth="linear",
        changepoint_range=0.8,
        changepoint_prior_scale=0.05,

        yearly_seasonality="auto",
        weekly_seasonality="auto",
        daily_seasonality="auto",

        seasonality_mode="additive",
        seasonality_prior_scale=10.0,
        holidays_prior_scale=10.0,

        interval_width=0.8,
        uncertainty_samples=1000,

        scaling="absmax",
        holidays_mode="additive",

        seasons=[],
        changepoints=[]
    )

def build_prophet_from_settings(settings: ProphetModelSetting):
    model = Prophet(
        growth=settings.growth,
        changepoint_range=settings.changepoint_range,
        yearly_seasonality=settings.yearly_seasonality,
        weekly_seasonality=settings.weekly_seasonality,
        daily_seasonality=settings.daily_seasonality,
        seasonality_mode=settings.seasonality_mode,
        seasonality_prior_scale=settings.seasonality_prior_scale,
        holidays_prior_scale=settings.holidays_prior_scale,
        changepoint_prior_scale=settings.changepoint_prior_scale,
        interval_width=settings.interval_width,
        uncertainty_samples=settings.uncertainty_samples,
        scaling=settings.scaling,
        holidays_mode=settings.holidays_mode
    )
    for s in settings.seasons:
        model.add_seasonality(
            name=s.name,
            period=s.period,
            fourier_order=s.fourier_order,
            prior_scale=s.prior_scale,
            mode=s.mode
        )

    if settings.changepoints:
        model.changepoints = pd.to_datetime([c.ds for c in settings.changepoints])
    return model


class ProphetModelRepository:
    def __init__(self, cur: Cursor):
        self.cur = cur

    def does_product_have_model(self, product_id: str) -> bool:
        query = """
            SELECT EXISTS(
                SELECT 1
                FROM prophet_model
                WHERE product_id = %s
            );
        """

        self.cur.execute(query, (product_id,))
        result = self.cur.fetchone()

        return result[0] if result else False

    def get_model_by_product_id(self, product_id: str) -> ProphetModel | None:
        query = """
            SELECT
                id,
                product_id,
                name,
                file_path,
                active,
                trained_at
            FROM prophet_model
            WHERE product_id = %s;
        """

        self.cur.execute(query, (product_id,))
        result = self.cur.fetchone()

        if not result:
            return None

        return ProphetModel(
            id=result[0],
            product_id=result[1],
            name=result[2],
            model_path=result[3],
            active=result[4],
            trained_at=result[5]
        )
        
    def save_model_settings(self, setting: ProphetModelSetting):
        self.cur.execute("""
            INSERT INTO prophet_model_setting (
                id,
                prophet_model_id,
                growth,
                changepoint_range,
                changepoint_prior_scale,

                yearly_seasonality,
                weekly_seasonality,
                daily_seasonality,

                seasonality_mode,
                seasonality_prior_scale,
                holidays_prior_scale,

                interval_width,
                uncertainty_samples,

                scaling,
                holidays_mode
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id)
            DO UPDATE SET
                prophet_model_id = EXCLUDED.prophet_model_id,
                growth = EXCLUDED.growth,
                changepoint_range = EXCLUDED.changepoint_range,
                changepoint_prior_scale = EXCLUDED.changepoint_prior_scale,

                yearly_seasonality = EXCLUDED.yearly_seasonality,
                weekly_seasonality = EXCLUDED.weekly_seasonality,
                daily_seasonality = EXCLUDED.daily_seasonality,

                seasonality_mode = EXCLUDED.seasonality_mode,
                seasonality_prior_scale = EXCLUDED.seasonality_prior_scale,
                holidays_prior_scale = EXCLUDED.holidays_prior_scale,

                interval_width = EXCLUDED.interval_width,
                uncertainty_samples = EXCLUDED.uncertainty_samples,

                scaling = EXCLUDED.scaling,
                holidays_mode = EXCLUDED.holidays_mode
        """, (
            setting.id,
            setting.prophet_model_id,
            setting.growth,
            setting.changepoint_range,
            setting.changepoint_prior_scale,

            setting.yearly_seasonality,
            setting.weekly_seasonality,
            setting.daily_seasonality,

            setting.seasonality_mode,
            setting.seasonality_prior_scale,
            setting.holidays_prior_scale,

            setting.interval_width,
            setting.uncertainty_samples,

            setting.scaling,
            setting.holidays_mode
        ))

    def get_model_settings_by_product_id(self, product_id: str) -> ProphetModelSetting | None:
        query = """
            SELECT
                id,
                prophet_model_id,
                growth,
                changepoint_range,
                changepoint_prior_scale,

                yearly_seasonality,
                weekly_seasonality,
                daily_seasonality,

                seasonality_mode,
                seasonality_prior_scale,
                holidays_prior_scale,

                interval_width,
                uncertainty_samples,

                scaling,
                holidays_mode
            FROM prophet_model_setting
            WHERE prophet_model_id = (
                SELECT id FROM prophet_model WHERE product_id = %s
            );
        """

        self.cur.execute(query, (product_id,))
        row = self.cur.fetchone()

        if not row:
            return None

        setting_id = row[0]
        model_id = row[1]

        self.cur.execute("""
            SELECT id, model_setting_id, name, period, fourier_order, prior_scale, mode
            FROM prophet_model_seasonality
            WHERE model_setting_id = %s;
        """, (setting_id,))
        seasons_rows = self.cur.fetchall()

        seasons = [
            ProphetSeasonality(
                id=r[0],
                model_setting_id=r[1],
                name=r[2],
                period=float(r[3]),
                fourier_order=r[4],
                prior_scale=r[5],
                mode=r[6]
            )
            for r in seasons_rows
        ]

        self.cur.execute("""
            SELECT id, model_setting_id, ds
            FROM prophet_model_changepoint
            WHERE model_setting_id = %s;
        """, (setting_id,))
        cp_rows = self.cur.fetchall()

        changepoints = [
            ProphetChangepoint(
                id=r[0],
                model_setting_id=r[1],
                ds=r[2]
            )
            for r in cp_rows
        ]

        return ProphetModelSetting(
            id=setting_id,
            prophet_model_id=model_id,

            growth=row[2],
            changepoint_range=row[3],
            changepoint_prior_scale=row[4],

            yearly_seasonality=row[5],
            weekly_seasonality=row[6],
            daily_seasonality=row[7],

            seasonality_mode=row[8],
            seasonality_prior_scale=row[9],
            holidays_prior_scale=row[10],

            interval_width=row[11],
            uncertainty_samples=row[12],

            scaling=row[13],
            holidays_mode=row[14],

            seasons=seasons,
            changepoints=changepoints
        )

    def save(self, model: ProphetModel):
        query = """
            INSERT INTO prophet_model (
                id,
                product_id,
                name,
                file_path,
                active,
                trained_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE SET
                product_id = EXCLUDED.product_id,
                name = EXCLUDED.name,
                file_path = EXCLUDED.file_path,
                active = EXCLUDED.active,
                trained_at = EXCLUDED.trained_at;
        """

        self.cur.execute(query, (
            model.id,
            model.product_id,
            model.name,
            model.model_path,
            model.active,
            model.trained_at
        ))
