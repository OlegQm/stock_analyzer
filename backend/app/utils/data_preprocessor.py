import pandas as pd
import ta
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import os
from app.utils.data_collector import get_stock_data

def calculate_technical_indicators(data, indicators):
    """Рассчитать технические индикаторы для данных акции"""
    # Преобразуем список словарей обратно в DataFrame
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    result = {}
    
    if "sma" in indicators:
        # Simple Moving Average
        result["sma_20"] = ta.trend.sma_indicator(df['Close'], window=20).round(2).fillna(0).tolist()
        result["sma_50"] = ta.trend.sma_indicator(df['Close'], window=50).round(2).fillna(0).tolist()
        result["sma_200"] = ta.trend.sma_indicator(df['Close'], window=200).round(2).fillna(0).tolist()
    
    if "ema" in indicators:
        # Exponential Moving Average
        result["ema_20"] = ta.trend.ema_indicator(df['Close'], window=20).round(2).fillna(0).tolist()
        result["ema_50"] = ta.trend.ema_indicator(df['Close'], window=50).round(2).fillna(0).tolist()
    
    if "rsi" in indicators:
        # Relative Strength Index
        result["rsi_14"] = ta.momentum.rsi(df['Close'], window=14).round(2).fillna(0).tolist()
    
    if "macd" in indicators:
        # MACD
        macd = ta.trend.MACD(df['Close'])
        result["macd_line"] = macd.macd().round(2).fillna(0).tolist()
        result["macd_signal"] = macd.macd_signal().round(2).fillna(0).tolist()
        result["macd_histogram"] = macd.macd_diff().round(2).fillna(0).tolist()
    
    if "bollinger" in indicators:
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        result["bollinger_high"] = bollinger.bollinger_hband().round(2).fillna(0).tolist()
        result["bollinger_mid"] = bollinger.bollinger_mavg().round(2).fillna(0).tolist()
        result["bollinger_low"] = bollinger.bollinger_lband().round(2).fillna(0).tolist()
    
    return result

def analyze_with_nlp(query, symbols, period="1y"):
    """Анализ акций с помощью NLP"""
    # Получаем данные для всех запрошенных символов
    all_data = {}
    for symbol in symbols:
        all_data[symbol] = get_stock_data(symbol, period)
    
    # Создаем сводку данных для LLM
    data_summary = ""
    for symbol, data in all_data.items():
        df = pd.DataFrame(data)
        first_date = df['Date'].iloc[0]
        last_date = df['Date'].iloc[-1]
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        change_pct = ((end_price - start_price) / start_price) * 100
        
        data_summary += f"Symbol: {symbol}\n"
        data_summary += f"Period: {first_date} to {last_date}\n"
        data_summary += f"Starting price: ${start_price:.2f}\n"
        data_summary += f"Ending price: ${end_price:.2f}\n"
        data_summary += f"Change: {change_pct:.2f}%\n"
        data_summary += f"Highest price: ${df['High'].max():.2f}\n"
        data_summary += f"Lowest price: ${df['Low'].min():.2f}\n"
        data_summary += f"Average volume: {df['Volume'].mean():.0f}\n\n"
    
    # Используем LangChain для анализа
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = ChatPromptTemplate.from_template(
        """Ты финансовый аналитик. Проанализируй следующие данные акций и ответь на запрос.
        
        Данные акций:
        {data_summary}
        
        Запрос пользователя: {query}
        
        Предоставь подробный анализ, основанный на данных. Если возможно, включи рекомендации 
        и выводы. Не придумывай информацию, которой нет в данных."""
    )
    
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"data_summary": data_summary, "query": query})
    
    return {
        "query": query,
        "symbols": symbols,
        "period": period,
        "analysis": result
    }
