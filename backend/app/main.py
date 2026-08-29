from fastapi import FastAPI

from app.database import Base, engine

from app.models.user import User

from app.routes.inspection import (
    router as inspection_router
)

from app.routes.analytics import (
    router as analytics_router
)

from app.routes.auth import (
    router as auth_router
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="VisionInspect AI",
    version="1.0.0"
)


app.include_router(
    inspection_router
)

app.include_router(
    analytics_router
)

app.include_router(
    auth_router
)


@app.get("/")
def home():

    return {
        "message": "VisionInspect AI Backend is Running"
    }
