import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class MarketData:
    def __init__(self):
        self.sp500_symbol = "^GSPC"
    
    def get_market_return(self) -> float:
        """Get S&P 500 daily return"""
        try:
            sp500 = yf.Ticker(self.sp500_symbol)
            hist = sp500.history(period="2d")
            if len(hist) >= 2:
                yesterday_close = hist['Close'].iloc[-2]
                today_close = hist['Close'].iloc[-1]
                return ((today_close - yesterday_close) / yesterday_close) * 100
            return 0.0
        except Exception as e:
            print(f"Error getting market return: {str(e)}")
            return 0.0
    
    def get_stock_data(self, symbol: str) -> dict:
        """Get detailed stock data with real-time price"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            live_price = stock.history(period='1d', interval='1m').iloc[-1]['Close']
            
            return {
                'price': live_price,
                'change': info.get('regularMarketChangePercent', 0.0),
                'volume': info.get('regularMarketVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 0.0),
                'currency': info.get('currency', 'USD'),
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            raise Exception(f"Error fetching stock data: {str(e)}")

    def get_real_time_quote(self, symbol: str) -> str:
        """Get real-time quote with formatted output"""
        try:
            data = self.get_stock_data(symbol)
            return f"${data['price']:.2f} {data['currency']} ({data['change']:.2f}%) - Actualizado: {data['timestamp']}"
        except Exception as e:
            return f"Error obteniendo cotización: {str(e)}"
