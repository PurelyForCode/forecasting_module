from fastapi import FastAPI
from api.routes_forecast import forecast_router

app = FastAPI()

app.include_router(forecast_router, prefix="/api/forecasts", tags=["forecast"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="localhost", port=8000, reload=True)
