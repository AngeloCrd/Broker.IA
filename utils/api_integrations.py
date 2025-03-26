
import requests
from typing import Dict, Any
import streamlit as st

class APIIntegrations:
    def __init__(self):
        self.endpoints = {
            'alpha_vantage': 'https://www.alphavantage.co/query',
            'coingecko': 'https://api.coingecko.com/api/v3',
            'polygon': 'https://api.polygon.io/v2'
        }

    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Obtener datos de acciones usando Alpha Vantage"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': st.secrets.get("ALPHA_VANTAGE_KEY", "")
        }
        response = requests.get(self.endpoints['alpha_vantage'], params=params)
        return response.json()

    def get_crypto_data(self, crypto_id: str) -> Dict[str, Any]:
        """Obtener datos de criptomonedas usando CoinGecko"""
        response = requests.get(f"{self.endpoints['coingecko']}/simple/price",
            params={'ids': crypto_id, 'vs_currencies': 'usd'})
        return response.json()

    def get_real_time_data(self, symbol: str) -> Dict[str, Any]:
        """Obtener datos en tiempo real usando Polygon"""
        headers = {'Authorization': f"Bearer {st.secrets.get('POLYGON_KEY', '')}"}
        response = requests.get(
            f"{self.endpoints['polygon']}/aggs/ticker/{symbol}/prev",
            headers=headers
        )
        return response.json()
