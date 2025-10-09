from fastapi import FastAPI
from .forecasts.forecast_router import forecast_router


app = FastAPI()

@app.get("/healthcheck")
def healthcheck():
    return {"message": "ok"}

app.include_router(forecast_router, prefix="/forecasts")


