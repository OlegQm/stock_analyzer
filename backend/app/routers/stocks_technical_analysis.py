from fastapi import APIRouter
from app.models import TechnicalAnalysisRequest
from app.services.stocks_technical_analysis_service import technical_analysis_service

router = APIRouter()

@router.post("/stocks/technical-analysis")
async def technical_analysis(request: TechnicalAnalysisRequest):
    """Perform technical analysis of a stock"""
    return await technical_analysis_service(request)
