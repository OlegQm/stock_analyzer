from fastapi import HTTPException
from app.models import VisualizationRequest
from app.utils.visualization import generate_chart_data

async def create_visualization_service(request: VisualizationRequest):
    """Создать данные для визуализации"""
    try:
        chart_data = generate_chart_data(
            request.symbols,
            request.chart_type,
            request.period,
            request.interval,
            request.indicators
        )
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))