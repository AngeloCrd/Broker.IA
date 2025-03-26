import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .portfolio import Portfolio
from .market_data import MarketData
from .ai_advisor import AIAdvisor
import json
from openai import OpenAI

class RecommendationEngine:
    def __init__(self):
        self.market_data = MarketData()
        self.ai_advisor = AIAdvisor()
        self.openai = OpenAI()

    def analyze_portfolio_risk(self, portfolio: Portfolio) -> dict:
        """Analizar el riesgo del portafolio actual"""
        positions = portfolio.get_positions()
        if positions.empty:
            return {
                "risk_level": "N/A",
                "diversification_score": 0,
                "concentration_risk": "N/A"
            }

        # Calcular métricas de riesgo
        total_value = positions['Market Value'].sum()
        position_weights = positions['Market Value'] / total_value

        # Riesgo de concentración
        max_weight = position_weights.max()
        concentration_risk = "Alto" if max_weight > 0.3 else "Medio" if max_weight > 0.15 else "Bajo"

        # Score de diversificación (0-100)
        num_positions = len(positions)
        sector_diversity = len(positions['Symbol'].unique())
        diversification_score = min(100, (num_positions * 10) + (sector_diversity * 5))

        # Nivel de riesgo general
        risk_scores = {
            "concentration": 1 if concentration_risk == "Bajo" else 2 if concentration_risk == "Medio" else 3,
            "diversification": 1 if diversification_score >= 70 else 2 if diversification_score >= 40 else 3
        }
        avg_risk = sum(risk_scores.values()) / len(risk_scores)
        risk_level = "Bajo" if avg_risk <= 1.5 else "Medio" if avg_risk <= 2.5 else "Alto"

        return {
            "risk_level": risk_level,
            "diversification_score": diversification_score,
            "concentration_risk": concentration_risk
        }

    def get_ai_market_analysis(self, portfolio: Portfolio) -> str:
        """Obtener análisis de mercado avanzado usando GPT-4"""
        try:
            positions = portfolio.get_positions()
            market_data = self.market_data.get_market_data()

            # Obtener datos históricos y fundamentales para cada posición
            historical_data = {}
            fundamental_data = {}
            for symbol in positions['Symbol'].unique():
                historical_data[symbol] = self.market_data.get_historical_data(symbol, days=365)
                fundamental_data[symbol] = self.market_data.get_fundamental_data(symbol)

            prompt = f"""
            Por favor, realiza un análisis detallado y profundo del siguiente portafolio y condiciones de mercado:

            PORTAFOLIO ACTUAL:
            {positions.to_string()}

            DATOS DE MERCADO ACTUALES:
            {json.dumps(market_data, indent=2)}

            DATOS HISTÓRICOS Y FUNDAMENTALES:
            {json.dumps(fundamental_data, indent=2)}

            Proporciona un análisis exhaustivo que incluya:

            1. ANÁLISIS FUNDAMENTAL:
            - Valoración de cada activo (P/E, P/B, márgenes)
            - Salud financiera de las empresas
            - Tendencias de crecimiento

            2. ANÁLISIS TÉCNICO:
            - Tendencias de precio a corto y largo plazo
            - Patrones técnicos relevantes
            - Niveles de soporte y resistencia clave

            3. ANÁLISIS DE MERCADO:
            - Condiciones macroeconómicas actuales
            - Tendencias sectoriales
            - Eventos geopolíticos relevantes

            4. GESTIÓN DE RIESGOS:
            - Identificación de riesgos específicos
            - Correlaciones entre activos
            - Factores de riesgo sistemático

            5. OPORTUNIDADES IDENTIFICADAS:
            - Oportunidades de corto plazo
            - Posicionamiento estratégico
            - Potencial de crecimiento

            6. RECOMENDACIONES ESTRATÉGICAS:
            - Ajustes sugeridos al portafolio
            - Nuevas oportunidades de inversión
            - Estrategias de cobertura

            Formato: Análisis estructurado con puntos clave, datos cuantitativos y explicaciones detalladas.
            Incluye cifras específicas y justificación para cada recomendación.
            """

            response = self.openai.chat.completions.create(
                model="gpt-4",  # Último modelo de OpenAI
                messages=[{
                    "role": "system",
                    "content": """Eres un analista financiero experto con más de 20 años de experiencia.
                    Proporcionas análisis detallados y basados en datos, siempre incluyendo:
                    - Métricas específicas y cuantitativas
                    - Contexto histórico y comparativo
                    - Proyecciones fundamentadas
                    - Riesgos y oportunidades concretas"""
                },
                {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error en análisis de IA: {str(e)}"

    def generate_personalized_recommendations(self, portfolio: Portfolio, risk_profile: dict) -> dict:
        """Generar recomendaciones personalizadas basadas en IA"""
        try:
            current_positions = portfolio.get_positions()
            risk_analysis = self.analyze_portfolio_risk(portfolio)
            market_analysis = self.get_ai_market_analysis(portfolio)

            prompt = f"""
            Basándote en la siguiente información, genera recomendaciones de inversión altamente personalizadas:

            PERFIL DE INVERSOR:
            Perfil de Riesgo: {risk_profile['profile']}
            Score de Riesgo: {risk_profile['score']}

            ANÁLISIS DE RIESGO ACTUAL:
            {json.dumps(risk_analysis, indent=2)}

            POSICIONES ACTUALES:
            {current_positions.to_string()}

            ANÁLISIS DE MERCADO:
            {market_analysis}

            Proporciona recomendaciones específicas para:
            1. Rebalanceo de portafolio (con porcentajes específicos)
            2. Nuevas oportunidades de inversión (con puntos de entrada)
            3. Gestión de riesgos (estrategias concretas)
            4. Optimización de rendimiento
            5. Estrategias de timing de mercado
            6. Diversificación y cobertura

            Para cada recomendación, incluye:
            - Justificación detallada
            - Métricas relevantes
            - Temporalidad esperada
            - Riesgos asociados
            - Plan de implementación
            """

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "system",
                    "content": """Eres un asesor financiero experto que proporciona recomendaciones 
                    personalizadas detalladas y accionables. Tus recomendaciones siempre incluyen:
                    - Acciones específicas a tomar
                    - Datos cuantitativos
                    - Plazos temporales
                    - Gestión de riesgos"""
                },
                {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2000
            )

            recommendations = response.choices[0].message.content
            return {
                "ai_recommendations": recommendations,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            return {
                "error": f"Error generando recomendaciones: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def generate_trade_recommendations(self, portfolio: Portfolio) -> list:
        """Generar recomendaciones específicas de trading"""
        positions = portfolio.get_positions()
        recommendations = []
        
        if positions.empty:
            return [{
                "type": "INITIAL",
                "action": "DIVERSIFY",
                "description": "Considere iniciar posiciones en diferentes sectores del mercado para construir un portafolio diversificado."
            }]
        
        # Analizar cada posición
        for _, position in positions.iterrows():
            symbol = position['Symbol']
            current_price = position['Current Price']
            market_value = position['Market Value']
            
            # Obtener datos de mercado adicionales
            try:
                stock_data = self.market_data.get_stock_data(symbol)
                
                # Analizar métricas
                pe_ratio = stock_data.get('pe_ratio', 0)
                price_change = stock_data.get('change', 0)
                
                # Generar recomendación basada en métricas
                if price_change < -5 and pe_ratio < 15:
                    recommendations.append({
                        "type": "BUY",
                        "symbol": symbol,
                        "reason": "Oportunidad de compra: Caída significativa de precio y valuación atractiva",
                        "metrics": {
                            "price_change": f"{price_change:.2f}%",
                            "pe_ratio": pe_ratio
                        }
                    })
                elif price_change > 10 and pe_ratio > 30:
                    recommendations.append({
                        "type": "SELL",
                        "symbol": symbol,
                        "reason": "Considerar toma de ganancias: Fuerte subida y valuación elevada",
                        "metrics": {
                            "price_change": f"{price_change:.2f}%",
                            "pe_ratio": pe_ratio
                        }
                    })
                
            except Exception:
                continue
        
        return recommendations
    

    def get_portfolio_recommendations(self, portfolio: Portfolio) -> dict:
        """Obtener recomendaciones completas para el portafolio"""
        # Análisis de riesgo
        risk_analysis = self.analyze_portfolio_risk(portfolio)

        # Análisis de mercado avanzado con IA
        market_analysis = self.get_ai_market_analysis(portfolio)

        # Recomendaciones personalizadas
        risk_profile = {'profile': 'Moderado', 'score': 15} # Replace with actual risk profile retrieval
        personalized_recs = self.generate_personalized_recommendations(portfolio, risk_profile)

        # Recomendaciones de trading
        trade_recommendations = self.generate_trade_recommendations(portfolio)

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_analysis": risk_analysis,
            "market_analysis": market_analysis,
            "personalized_recommendations": personalized_recs,
            "trade_recommendations": trade_recommendations
        }