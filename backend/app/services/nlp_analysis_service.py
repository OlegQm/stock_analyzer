from fastapi import HTTPException
from app.models import NLPAnalysisRequest
from app.utils.data_preprocessor import analyze_with_nlp

async def nlp_analysis_service(request: NLPAnalysisRequest):
    """Analyze stocks using NLP"""
    try:
        result = analyze_with_nlp(request.query, request.symbols, request.period)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
