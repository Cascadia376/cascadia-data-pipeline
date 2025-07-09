from fastapi import FastAPI
from .core.config import settings
from .core.database import db
from .api.v1.router import api_router

app = FastAPI(title="Cascadia Retail API")

@app.on_event("startup")
async def startup_event():
    await db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await db.disconnect()

app.include_router(api_router, prefix="/api/v1")
