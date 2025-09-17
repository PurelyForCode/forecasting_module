from fastapi import FastAPI
from .forecasts.forecast_router import forecast_router


app = FastAPI()
@app.get("/")
def healthcheck():
    print("ok")
    return {"message": "ok"}

app.include_router(forecast_router, prefix="/forecasts")


