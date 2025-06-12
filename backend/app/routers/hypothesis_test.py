from fastapi import APIRouter
from app.models import HypothesisTestRequest
from app.services.hypothesis_test_service import hypothesis_test_service

router = APIRouter()

@router.post("/stocks/hypothesis-test")
async def hypothesis_test(request: HypothesisTestRequest):
    """Выполнить статистический тест гипотезы"""
    return await hypothesis_test_service(request)
