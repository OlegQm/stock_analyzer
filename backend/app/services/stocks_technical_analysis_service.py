from fastapi import HTTPException
from app.models import TechnicalAnalysisRequest
from app.utils.data_collector import get_stock_data
from app.utils.data_preprocessor import calculate_technical_indicators

async def technical_analysis_service(request: TechnicalAnalysisRequest):
    """Perform technical analysis of a stock"""
    try:
        data = get_stock_data(request.symbol, request.period, request.interval)
        indicators = calculate_technical_indicators(data, request.indicators)
        return {
            "symbol": request.symbol,
            "indicators": indicators
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))