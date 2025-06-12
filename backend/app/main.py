from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    stocks_visualization,
    nlp_analysis,
    hypothesis_test,
    stocks_technical_analysis,
    stocks_data,
    stocks_available
)

app = FastAPI(
    title="Financial Data Analysis API",
    description="API for collecting and analyzing financial data from Yahoo Finance",
    root_path="/",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

api_router.include_router(
    stocks_visualization.router,
    tags=["Stocks Visualization"]
)
api_router.include_router(
    nlp_analysis.router,
    tags=["NLP Analysis"]
)
api_router.include_router(
    hypothesis_test.router,
    tags=["Hypothesis Testing"]
)
api_router.include_router(
    stocks_technical_analysis.router,
    tags=["Stocks Technical Analysis"]
)
api_router.include_router(
    stocks_data.router,
    tags=["Stocks Data"]
)
api_router.include_router(
    stocks_available.router,
    tags=["Available Stocks"]
)

app.include_router(api_router)
