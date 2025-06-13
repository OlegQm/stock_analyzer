from app.utils.data_collector import get_stock_data
from app.utils.data_preprocessor import calculate_technical_indicators
import pandas as pd

def generate_chart_data(symbols, chart_type, period="1y", interval="1d", indicators=None):
    """Create data for visualization"""
    result = {
        "chart_type": chart_type,
        "symbols": symbols,
        "period": period,
        "interval": interval,
        "data": []
    }

    try:
        if chart_type == "price":
            for symbol in symbols:
                data = get_stock_data(symbol, period, interval)
                df = pd.DataFrame(data)

                if indicators:
                    tech_indicators = calculate_technical_indicators(data, indicators)
                    indicator_data = {}
                    for indicator_name, indicator_values in tech_indicators.items():
                        indicator_data[indicator_name] = indicator_values

                    result["data"].append({
                        "symbol": symbol,
                        "dates": df['Date'].tolist(),
                        "prices": df['Close'].tolist(),
                        "volumes": df['Volume'].tolist(),
                        "indicators": indicator_data
                    })
                else:
                    result["data"].append({
                        "symbol": symbol,
                        "dates": df['Date'].tolist(),
                        "prices": df['Close'].tolist(),
                        "volumes": df['Volume'].tolist()
                    })

        elif chart_type == "returns":
            for symbol in symbols:
                data = get_stock_data(symbol, period, interval)
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                df['Returns'] = df['Close'].pct_change().fillna(0)
                df['Cumulative_Returns'] = (1 + df['Returns']).cumprod() - 1

                df = df.reset_index()
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

                result["data"].append({
                    "symbol": symbol,
                    "dates": df['Date'].tolist(),
                    "daily_returns": df['Returns'].round(4).tolist(),
                    "cumulative_returns": df['Cumulative_Returns'].round(4).tolist()
                })

        elif chart_type == "correlation":
            all_returns = pd.DataFrame()

            for symbol in symbols:
                data = get_stock_data(symbol, period, interval)
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                all_returns[symbol] = df['Close'].pct_change().fillna(0)
            corr_matrix = all_returns.corr().round(2)
            corr_data = []
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols):
                    corr_data.append({
                        "x": symbol1,
                        "y": symbol2,
                        "value": corr_matrix.iloc[i, j]
                    })

            result["data"] = corr_data

        else:
            raise ValueError(f"Unknown chart type: {chart_type}")

    except Exception as e:
        result["error"] = str(e)

    return result
