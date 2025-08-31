from fastapi import FastAPI

from src.api.routers.data import router as data_router

app = FastAPI(title="Fonte API")
app.include_router(data_router)