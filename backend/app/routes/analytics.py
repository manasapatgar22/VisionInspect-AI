from fastapi import APIRouter

from app.services.inspection_history import (
    get_inspection_history,
    get_inspection_statistics
)


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get("/history")
def inspection_history():

    return {
        "inspections": get_inspection_history()
    }


@router.get("/statistics")
def inspection_statistics():

    return get_inspection_statistics()
