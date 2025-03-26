import streamlit as st
from datetime import datetime
from .portfolio import Portfolio
from .market_data import MarketData
from .ai_advisor import AIAdvisor
from .news import NewsService

class ReportGenerator:
    def __init__(self):
        self.market_data = MarketData()
        self.ai_advisor = AIAdvisor()
        self.news_service = NewsService()

    def _format_currency(self, value: float) -> str:
        """Formatear valores monetarios"""
        return f"${value:,.2f}"

    def _format_percentage(self, value: float) -> str:
        """Formatear porcentajes"""
        return f"{value:,.2f}%"

    def generate_portfolio_analysis(self, portfolio: Portfolio) -> str:
        """Generar análisis detallado del portafolio"""
        positions = portfolio.get_positions()
        total_value = portfolio.get_total_value()
        performance_data = portfolio.get_performance_history()

        # Calcular métricas adicionales
        total_gain_loss = positions['Gain/Loss'].sum() if not positions.empty else 0
        total_return = (total_gain_loss / total_value * 100) if total_value > 0 else 0
        best_performer = positions.nlargest(1, 'Return %')['Symbol'].iloc[0] if not positions.empty else None
        worst_performer = positions.nsmallest(1, 'Return %')['Symbol'].iloc[0] if not positions.empty else None

        portfolio_summary = f"""
        # 📊 Análisis de Portafolio: {portfolio.name}

        ## 💰 Resumen General
        - **Valor Total del Portafolio:** {self._format_currency(total_value)}
        - **Ganancia/Pérdida Total:** {self._format_currency(total_gain_loss)}
        - **Rendimiento Total:** {self._format_percentage(total_return)}
        - **Número de Posiciones:** {len(positions)}

        ## 🔍 Análisis de Rendimiento
        - **Mejor Rendimiento:** {best_performer if best_performer else 'N/A'}
        - **Peor Rendimiento:** {worst_performer if worst_performer else 'N/A'}

        ## 📈 Desglose de Posiciones
        """

        if not positions.empty:
            for _, position in positions.iterrows():
                portfolio_summary += f"""
                ### {position['Symbol']}
                - **Acciones:** {position['Shares']}
                - **Precio Actual:** {self._format_currency(position['Current Price'])}
                - **Valor de Mercado:** {self._format_currency(position['Market Value'])}
                - **Ganancia/Pérdida:** {self._format_currency(position['Gain/Loss'])}
                - **Rendimiento:** {self._format_percentage(position['Return %'])}
                """

        return portfolio_summary

    def generate_market_analysis(self) -> str:
        """Generar análisis del mercado"""
        sp500_return = self.market_data.get_market_return()
        news = self.news_service.get_market_news(limit=5)

        market_analysis = f"""
        # 📈 Análisis de Mercado

        ## 📊 Indicadores Clave
        - **S&P 500 (Hoy):** {self._format_percentage(sp500_return)}

        ## 📰 Noticias Relevantes y Sentimiento del Mercado
        """

        if news:
            for article in news:
                sentiment = "positivo 📈" if article['sentiment'] > 0 else "negativo 📉" if article['sentiment'] < 0 else "neutral ⚖️"
                market_analysis += f"""
                - **{article['title']}**
                  * Sentimiento: {sentiment}
                  * Fuente: {article['source']}
                """
        else:
            market_analysis += "\n*No hay noticias relevantes disponibles en este momento.*"

        return market_analysis

    def generate_ai_recommendations(self, portfolio: Portfolio) -> str:
        """Generar recomendaciones personalizadas usando IA"""
        positions = portfolio.get_positions()
        symbols = positions['Symbol'].tolist() if not positions.empty else []

        analysis_prompt = f"""
        Por favor, analiza este portafolio y proporciona recomendaciones estratégicas detalladas:

        Portafolio: {portfolio.name}
        Símbolos: {', '.join(symbols)}
        Valor Total: {self._format_currency(portfolio.get_total_value())}

        Incluye:
        1. Evaluación de la diversificación actual
        2. Sugerencias de rebalanceo si es necesario
        3. Oportunidades de crecimiento
        4. Análisis de riesgos
        5. Recomendaciones específicas para cada posición
        """

        recommendations = self.ai_advisor.get_advice(analysis_prompt)
        return f"""
        # 🤖 Recomendaciones Personalizadas de IA

        {recommendations}
        """

    def generate_complete_report(self, portfolio: Portfolio) -> dict:
        """Generar informe completo"""
        report = {
            'title': f"Informe de Inversión - {portfolio.name}",
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'portfolio_analysis': self.generate_portfolio_analysis(portfolio),
            'market_analysis': self.generate_market_analysis(),
            'ai_recommendations': self.generate_ai_recommendations(portfolio),
        }

        return report