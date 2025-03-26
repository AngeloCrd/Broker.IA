import os
from openai import OpenAI
from .market_data import MarketData
from .news import NewsService
import streamlit as st

class AIAdvisor:
    def __init__(self):
        self.model = "gpt-3.5-turbo"  # Cambiado a gpt-3.5-turbo
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.market_data = MarketData()
        self.news_service = NewsService()

    def get_market_context(self):
        """Obtener contexto del mercado en tiempo real"""
        try:
            sp500_return = self.market_data.get_market_return()
            latest_news = self.news_service.get_market_news(limit=3)

            market_context = f"""
            Contexto actual del mercado:
            - S&P 500 hoy: {sp500_return:.2f}%

            Últimas noticias relevantes:
            """

            for news in latest_news:
                sentiment = "positivo" if news['sentiment'] > 0 else "negativo" if news['sentiment'] < 0 else "neutral"
                market_context += f"- {news['title']} (Sentimiento: {sentiment})\n"

            return market_context
        except Exception as e:
            return "No se pudo obtener el contexto del mercado en este momento."

    def get_advice(self, question: str) -> str:
        """Obtener asesoramiento financiero usando AI"""
        try:
            market_context = self.get_market_context()
            
            # Si la pregunta menciona un símbolo específico, obtener su cotización
            common_tickers = {
                "nvidia": "NVDA",
                "apple": "AAPL",
                "microsoft": "MSFT",
                "amazon": "AMZN",
                "google": "GOOGL",
                "meta": "META",
                "tesla": "TSLA"
            }
            
            stock_data = ""
            for company, ticker in common_tickers.items():
                if company.lower() in question.lower():
                    try:
                        quote = self.market_data.get_real_time_quote(ticker)
                        stock_data = f"\nCotización actual de {company.title()} ({ticker}): {quote}\n"
                        break
                    except:
                        pass
            
            market_context = f"{market_context}\n{stock_data}" if stock_data else market_context

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un asesor financiero profesional que responde en español.
                        Proporciona consejos claros, concisos y precisos basados en:
                        1. La pregunta del usuario
                        2. El contexto actual del mercado
                        3. Las últimas noticias relevantes y su sentimiento

                        Incluye advertencias cuando sea apropiado.
                        Mantén un tono profesional pero accesible."""
                    },
                    {
                        "role": "user",
                        "content": f"""Contexto del mercado:
                        {market_context}

                        Pregunta del usuario:
                        {question}"""
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al obtener asesoramiento: {str(e)}"