from fastapi import APIRouter

from app.services.stocks_available_service import get_available_stocks_service

router = APIRouter()

@router.get("/stocks/available")
async def get_available_stocks():
    """Get the list of stocks available for analysis"""
    return get_available_stocks_service()
