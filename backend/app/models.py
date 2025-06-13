from pydantic import BaseModel
from typing import List, Optional

class StockRequest(BaseModel):
    symbol: str
    period: str = "1y"
    interval: str = "1d"

class TechnicalAnalysisRequest(BaseModel):
    symbol: str
    period: str = "1y"
    interval: str = "1d"
    indicators: List[str] = ["sma", "ema", "rsi", "macd"]

class NLPAnalysisRequest(BaseModel):
    query: str
    symbols: List[str]
    period: str = "1y"

class HypothesisTestRequest(BaseModel):
    symbols: List[str]
    test_type: str
    period: str = "1y"
    alpha: float = 0.05

class VisualizationRequest(BaseModel):
    symbols: List[str]
    chart_type: str
    period: str = "1y"
    interval: str = "1d"
    indicators: Optional[List[str]] = None
