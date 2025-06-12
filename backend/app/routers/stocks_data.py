from fastapi import APIRouter
from app.models import StockRequest
from app.services.stocks_data_service import fetch_data

router = APIRouter()

@router.post("/stocks/data")
async def fetch_stock_data(request: StockRequest):
    """Получить исторические данные акции"""
    return fetch_data(request)
