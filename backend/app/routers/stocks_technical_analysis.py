from fastapi import APIRouter
from app.models import TechnicalAnalysisRequest
from app.services.stocks_technical_analysis_service import technical_analysis_service

router = APIRouter()

@router.post("/stocks/technical-analysis")
async def technical_analysis(request: TechnicalAnalysisRequest):
    """Выполнить технический анализ акции"""
    return await technical_analysis_service(request)
