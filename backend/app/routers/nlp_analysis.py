from fastapi import APIRouter
from app.models import NLPAnalysisRequest
from app.services.nlp_analysis_service import nlp_analysis_service

router = APIRouter()

@router.post("/stocks/nlp-analysis")
async def nlp_analysis(request: NLPAnalysisRequest):
    """Анализ акций с помощью NLP"""
    return await nlp_analysis_service(request)
