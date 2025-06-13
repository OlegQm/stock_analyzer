from fastapi import APIRouter
from app.models import VisualizationRequest
from app.services.stocks_visualization_service import create_visualization_service

router = APIRouter()

@router.post("/stocks/visualization")
async def create_visualization(request: VisualizationRequest):
    """Create data for visualization"""
    return await create_visualization_service(request)
