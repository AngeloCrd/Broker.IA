import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple

class RiskProfiler:
    def __init__(self):
        self.questions = [
            {
                "id": 1,
                "text": "¿Cuál es tu horizonte temporal de inversión?",
                "options": [
                    ("Menos de 1 año", 1),
                    ("1-3 años", 2),
                    ("3-5 años", 3),
                    ("5-10 años", 4),
                    ("Más de 10 años", 5)
                ]
            },
            {
                "id": 2,
                "text": "Si tus inversiones cayeran un 20% en un mes, ¿qué harías?",
                "options": [
                    ("Vender todo inmediatamente", 1),
                    ("Vender una parte", 2),
                    ("Esperar y no hacer nada", 3),
                    ("Comprar un poco más", 4),
                    ("Aprovechar para comprar mucho más", 5)
                ]
            },
            {
                "id": 3,
                "text": "¿Qué porcentaje de tus ahorros estás dispuesto a invertir?",
                "options": [
                    ("Menos del 10%", 1),
                    ("10-25%", 2),
                    ("25-50%", 3),
                    ("50-75%", 4),
                    ("Más del 75%", 5)
                ]
            },
            {
                "id": 4,
                "text": "¿Cuál es tu experiencia en inversiones?",
                "options": [
                    ("Ninguna", 1),
                    ("Algo de experiencia con fondos", 2),
                    ("Experiencia con acciones", 3),
                    ("Experiencia con derivados", 4),
                    ("Trader profesional", 5)
                ]
            },
            {
                "id": 5,
                "text": "¿Cuál es tu objetivo principal al invertir?",
                "options": [
                    ("Preservar mi capital", 1),
                    ("Obtener ingresos estables", 2),
                    ("Crecimiento moderado", 3),
                    ("Alto crecimiento", 4),
                    ("Máximo rendimiento posible", 5)
                ]
            }
        ]
        
        self.risk_profiles = {
            "Conservador": {
                "range": (5, 11),
                "description": "Prefieres inversiones seguras y estables. Tu prioridad es preservar el capital.",
                "recommended_assets": ["Bonos gubernamentales", "Depósitos", "Fondos monetarios"],
                "allocation": {
                    "Renta Fija": "70-80%",
                    "Renta Variable": "10-20%",
                    "Liquidez": "10%"
                }
            },
            "Moderado": {
                "range": (12, 18),
                "description": "Buscas un equilibrio entre seguridad y rendimiento.",
                "recommended_assets": ["Bonos corporativos", "ETFs diversificados", "Acciones blue chip"],
                "allocation": {
                    "Renta Fija": "40-60%",
                    "Renta Variable": "30-50%",
                    "Alternativos": "10%"
                }
            },
            "Equilibrado": {
                "range": (19, 22),
                "description": "Aceptas volatilidad moderada a cambio de mejores rendimientos.",
                "recommended_assets": ["Acciones", "ETFs sectoriales", "Bonos de alto rendimiento"],
                "allocation": {
                    "Renta Variable": "50-70%",
                    "Renta Fija": "20-40%",
                    "Alternativos": "10-20%"
                }
            },
            "Dinámico": {
                "range": (23, 25),
                "description": "Buscas maximizar el rendimiento y aceptas alta volatilidad.",
                "recommended_assets": ["Acciones growth", "ETFs apalancados", "Criptomonedas"],
                "allocation": {
                    "Renta Variable": "70-80%",
                    "Alternativos": "15-25%",
                    "Liquidez": "5%"
                }
            }
        }

    def calculate_profile(self, answers: Dict[int, int]) -> Dict:
        """Calcular el perfil de riesgo basado en las respuestas"""
        total_score = sum(answers.values())
        
        for profile, details in self.risk_profiles.items():
            if details["range"][0] <= total_score <= details["range"][1]:
                return {
                    "profile": profile,
                    "score": total_score,
                    **details
                }
        
        return self.risk_profiles["Moderado"]

    def render_quiz(self) -> Dict:
        """Renderizar el cuestionario de perfil de riesgo"""
        st.header("Descubre tu Perfil de Inversión")
        
        st.markdown("""
        <div style='
            padding: 1rem;
            background: rgba(49,51,63,0.1);
            border-radius: 10px;
            margin-bottom: 1rem;
        '>
            <h4>¿Por qué es importante conocer tu perfil?</h4>
            <p>Tu perfil de inversión determina la estrategia más adecuada para ti,
            considerando tus objetivos, tolerancia al riesgo y experiencia.</p>
        </div>
        """, unsafe_allow_html=True)

        answers = {}
        
        for question in self.questions:
            st.subheader(f"Pregunta {question['id']}")
            answers[question['id']] = st.radio(
                question['text'],
                options=range(len(question['options'])),
                format_func=lambda x: question['options'][x][0],
                horizontal=True,
                key=f"q_{question['id']}"
            ) + 1

        if st.button("Calcular Mi Perfil", use_container_width=True):
            profile_result = self.calculate_profile(answers)
            
            st.markdown("---")
            st.subheader("Resultados del Análisis")
            
            # Mostrar el perfil calculado
            col1, col2 = st.columns([2,1])
            
            with col1:
                st.markdown(f"""
                <div style='
                    padding: 1.5rem;
                    background: linear-gradient(145deg, rgba(49,51,63,0.1) 0%, rgba(49,51,63,0.05) 100%);
                    border-radius: 10px;
                    margin-bottom: 1rem;
                '>
                    <h3>Tu perfil es: {profile_result['profile']}</h3>
                    <p>{profile_result['description']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric(
                    "Puntuación de Riesgo",
                    profile_result['score'],
                    help="Puntuación basada en tus respuestas"
                )

            # Mostrar recomendaciones
            st.subheader("Recomendaciones de Inversión")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Activos Recomendados")
                for asset in profile_result['recommended_assets']:
                    st.markdown(f"- {asset}")
            
            with col2:
                st.markdown("### Asignación Sugerida")
                for asset_type, allocation in profile_result['allocation'].items():
                    st.markdown(f"- **{asset_type}:** {allocation}")

            return profile_result
        
        return None

    def get_profile_summary(self, profile_result: Dict) -> pd.DataFrame:
        """Generar resumen del perfil para el dashboard"""
        if not profile_result:
            return pd.DataFrame()
            
        data = {
            "Métrica": [
                "Perfil",
                "Puntuación",
                "Horizonte Temporal",
                "Riesgo Aceptado",
                "Objetivo Principal"
            ],
            "Valor": [
                profile_result['profile'],
                profile_result['score'],
                "Largo plazo" if profile_result['score'] > 15 else "Medio plazo",
                "Alto" if profile_result['score'] > 20 else "Medio",
                "Crecimiento" if profile_result['score'] > 15 else "Preservación"
            ]
        }
        
        return pd.DataFrame(data)
