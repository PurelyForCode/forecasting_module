import uvicorn
from forecasting_module.infra.web.app import app # type: ignore

if __name__ == "__main__":
    uvicorn.run("forecasting_module.infra.web.app:app", host="127.0.0.1", port=3001, reload=True)
