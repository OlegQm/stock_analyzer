from fastapi import HTTPException
from app.models import HypothesisTestRequest
from app.utils.hypothesis_testing import run_hypothesis_test

async def hypothesis_test_service(request: HypothesisTestRequest):
    """Выполнить статистический тест гипотезы"""
    try:
        result = run_hypothesis_test(
            request.symbols, 
            request.test_type, 
            request.period, 
            request.alpha
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
