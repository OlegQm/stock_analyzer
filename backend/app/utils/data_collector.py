import yfinance as yf

def get_stock_data(symbol, period="1y", interval="1d"):
    """Retrieve historical stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        df = df.reset_index()
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        for col in df.columns:
            if df[col].dtype == 'float64':
                df[col] = df[col].round(2)
        
        return df.to_dict(orient='records')
    except Exception as e:
        raise Exception(f"Error retrieving data for {symbol}: {str(e)}")

def get_stock_info(symbol):
    """Get stock information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        relevant_info = {
            'shortName': info.get('shortName', ''),
            'longName': info.get('longName', ''),
            'sector': info.get('sector', ''),
            'industry': info.get('industry', ''),
            'website': info.get('website', ''),
            'marketCap': info.get('marketCap', None),
            'trailingPE': info.get('trailingPE', None),
            'forwardPE': info.get('forwardPE', None),
            'dividendYield': info.get('dividendYield', None) * 100 if info.get('dividendYield') else None,
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', None),
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', None),
            'averageVolume': info.get('averageVolume', None),
            'regularMarketPrice': info.get('regularMarketPrice', None),
            'regularMarketChange': info.get('regularMarketChange', None),
            'regularMarketChangePercent': info.get('regularMarketChangePercent', None),
        }
        
        return relevant_info
    except Exception as e:
        raise Exception(f"Error retrieving info for {symbol}: {str(e)}")
    