import os
import requests
from datetime import datetime, timedelta
import streamlit as st
import json

class NewsService:
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.alpha_vantage_key:
            raise ValueError("Alpha Vantage API key not found")

    @st.cache_data(ttl=300)  # Cache por 5 minutos
    def _fetch_news(_self, limit: int = 10) -> list:
        """Función interna para obtener noticias (compatible con cache)"""
        try:
            # Construir URL con parámetros específicos
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "apikey": _self.alpha_vantage_key,
                "topics": "financial_markets",  # Simplificado a un solo tema
                "sort": "LATEST"
            }

            # Realizar la petición con timeout
            response = requests.get(url, params=params, timeout=10)

            # Verificar si la respuesta es exitosa
            if response.status_code != 200:
                return []

            # Parsear la respuesta JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                return []

            # Verificar mensajes de la API
            if 'Information' in data or 'Note' in data or 'feed' not in data:
                return []

            # Procesar las noticias
            news_items = []
            for item in data['feed'][:limit]:
                try:
                    # Formatear fecha
                    date_str = item.get('time_published', datetime.now().strftime('%Y%m%dT%H%M%S'))
                    date = datetime.strptime(date_str, '%Y%m%dT%H%M%S')

                    # Procesar sentimiento
                    sentiment = float(item.get('overall_sentiment_score', 0))

                    news_items.append({
                        'title': item.get('title', 'Sin título'),
                        'source': item.get('source', 'Fuente desconocida'),
                        'summary': item.get('summary', 'Sin resumen disponible'),
                        'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                        'sentiment': sentiment,
                        'url': item.get('url', '#')
                    })
                except Exception:
                    continue

            return news_items

        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.RequestException:
            return []
        except Exception:
            return []

    def get_market_news(self, limit: int = 10) -> list:
        """Método público para obtener noticias"""
        return self._fetch_news(limit)