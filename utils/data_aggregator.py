import yfinance as yf
from newsapi import NewsApiClient
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import pandas as pd

class DataAggregator:
    def __init__(self):
        """Initialize connections to various data sources"""
        self.newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

    def get_stock_data(self, symbol: str) -> Dict:
        """Get comprehensive stock data from multiple sources"""
        try:
            # Get data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Estructura la información
            return {
                "current_price": info.get("currentPrice", 0),
                "previous_close": info.get("previousClose", 0),
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "beta": info.get("beta", 0),
                "description": info.get("longBusinessSummary", "")
            }
        except Exception as e:
            st.error(f"Error obteniendo datos de {symbol}: {str(e)}")
            return {}

    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            return df
        except Exception as e:
            st.error(f"Error obteniendo datos históricos de {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_financial_news(self, query: str = "finance", days: int = 7) -> List[Dict]:
        """Get financial news from multiple sources"""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            # Get news from NewsAPI
            news_response = self.newsapi.get_everything(
                q=query,
                from_param=from_date,
                language='es',
                sort_by='relevancy'
            )

            news_items = []
            for article in news_response.get('articles', []):
                news_items.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'urlToImage': article.get('urlToImage', '')
                })

            return news_items
        except Exception as e:
            st.error(f"Error obteniendo noticias: {str(e)}")
            return []

    def get_market_movers(self) -> Dict:
        """Get market movers and trending stocks"""
        try:
            # List of major indices
            indices = ['^GSPC', '^IXIC', '^DJI']
            market_data = {}

            for index in indices:
                ticker = yf.Ticker(index)
                info = ticker.info
                market_data[index] = {
                    'name': info.get('shortName', ''),
                    'price': info.get('regularMarketPrice', 0),
                    'change': info.get('regularMarketChangePercent', 0)
                }

            return market_data
        except Exception as e:
            st.error(f"Error obteniendo datos del mercado: {str(e)}")
            return {}

    def get_sector_performance(self) -> Dict:
        """Get sector performance analysis"""
        try:
            sectors = [
                'XLF',  # Financial
                'XLK',  # Technology
                'XLV',  # Healthcare
                'XLE',  # Energy
                'XLI',  # Industrial
                'XLP',  # Consumer Staples
                'XLY'   # Consumer Discretionary
            ]

            sector_data = {}
            for sector in sectors:
                ticker = yf.Ticker(sector)
                info = ticker.info
                sector_data[sector] = {
                    'name': info.get('shortName', ''),
                    'change': info.get('regularMarketChangePercent', 0)
                }

            return sector_data
        except Exception as e:
            st.error(f"Error obteniendo rendimiento sectorial: {str(e)}")
            return {}