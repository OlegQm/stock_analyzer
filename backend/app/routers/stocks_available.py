from fastapi import APIRouter

from app.services.stocks_available_service import get_available_stocks_service

router = APIRouter()

@router.get("/stocks/available")
async def get_available_stocks():
    """Получить список доступных акций для анализа"""
    # В реальном приложении здесь можно возвращать список из базы данных
    # или из кэша, но для примера вернем несколько популярных акций
    return get_available_stocks_service()
