import requests
import os
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def get_available_stocks():
    """Получить список доступных акций"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/stocks/available", timeout=20)
        if response.status_code == 200:
            return response.json()["stocks"]
        else:
            st.error(f"Ошибка при получении списка акций: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Ошибка при подключении к API: {e}")
        return []

def get_stock_data(symbol, period="1y", interval="1d"):
    """Получить данные акции"""
    try:
        payload = {
            "symbol": symbol,
            "period": period,
            "interval": interval
        }
        response = requests.post(
            f"{BACKEND_URL}/api/stocks/data",
            json=payload,
            timeout=20
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при получении данных акции: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ошибка при подключении к API: {e}")
        return None

def get_technical_analysis(symbol, period="1y", interval="1d", indicators=None):
    """Получить технический анализ акции"""
    if indicators is None:
        indicators = ["sma", "ema", "rsi", "macd"]

    try:
        payload = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "indicators": indicators
        }
        response = requests.post(
            f"{BACKEND_URL}/api/stocks/technical-analysis",
            json=payload,
            timeout=20
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при получении технического анализа: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ошибка при подключении к API: {e}")
        return None

def get_nlp_analysis(query, symbols, period="1y"):
    """Получить NLP анализ акций"""
    try:
        payload = {
            "query": query,
            "symbols": symbols,
            "period": period
        }
        response = requests.post(
            f"{BACKEND_URL}/api/stocks/nlp-analysis",
            json=payload,
            timeout=20
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при получении NLP анализа: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ошибка при подключении к API: {e}")
        return None

def run_hypothesis_test(symbols, test_type, period="1y", alpha=0.05):
    """Выполнить тест гипотезы"""
    try:
        payload = {
            "symbols": symbols,
            "test_type": test_type,
            "period": period,
            "alpha": alpha
        }
        response = requests.post(
            f"{BACKEND_URL}/api/stocks/hypothesis-test",
            json=payload,
            timeout=20
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при выполнении теста гипотезы: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ошибка при подключении к API: {e}")
        return None

def get_visualization_data(
    symbols,
    chart_type,
    period="1y",
    interval="1d",
    indicators=None
):
    """Получить данные для визуализации"""
    try:
        payload = {
            "symbols": symbols,
            "chart_type": chart_type,
            "period": period,
            "interval": interval,
            "indicators": indicators
        }
        response = requests.post(
            f"{BACKEND_URL}/api/stocks/visualization",
            json=payload,
            timeout=20
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при получении данных для визуализации: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ошибка при подключении к API: {e}")
        return None
