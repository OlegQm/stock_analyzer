from fastapi import HTTPException
from app.utils.data_collector import get_stock_data, get_stock_info
from app.models import StockRequest

def fetch_data(request: StockRequest):
    try:
        data = get_stock_data(request.symbol, request.period, request.interval)
        info = get_stock_info(request.symbol)
        return {
            "symbol": request.symbol,
            "data": data,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))