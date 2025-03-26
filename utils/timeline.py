import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict

class InvestmentTimeline:
    def __init__(self):
        self.events = []

    def add_event(self, event: Dict):
        """Añadir un nuevo evento a la línea de tiempo"""
        self.events.append({
            **event,
            "date": datetime.strptime(event["date"], "%Y-%m-%d") if isinstance(event["date"], str) else event["date"]
        })
        self.events.sort(key=lambda x: x["date"])

    def get_default_events(self) -> List[Dict]:
        """Obtener eventos predeterminados para demostración"""
        return [
            {
                "date": datetime.now() - timedelta(days=30),
                "title": "Inicio del Viaje",
                "description": "Primera conexión con broker",
                "category": "milestone",
                "icon": "rocket"
            },
            {
                "date": datetime.now() - timedelta(days=25),
                "title": "Primer Análisis de Riesgo",
                "description": "Completaste tu perfil de inversor",
                "category": "assessment",
                "icon": "chart-line"
            },
            {
                "date": datetime.now() - timedelta(days=20),
                "title": "Primera Inversión",
                "description": "Realizaste tu primera operación",
                "category": "investment",
                "icon": "money-bill"
            },
            {
                "date": datetime.now() - timedelta(days=15),
                "title": "Diversificación",
                "description": "Portfolio diversificado en múltiples activos",
                "category": "strategy",
                "icon": "chart-pie"
            },
            {
                "date": datetime.now() - timedelta(days=10),
                "title": "Primer Objetivo Alcanzado",
                "description": "Superaste tu primer objetivo de rendimiento",
                "category": "achievement",
                "icon": "trophy"
            },
            {
                "date": datetime.now() - timedelta(days=5),
                "title": "Nuevo Nivel",
                "description": "Alcanzaste el nivel intermedio",
                "category": "level-up",
                "icon": "star"
            }
        ]

    def render_timeline(self):
        """Renderizar la línea de tiempo animada"""
        st.markdown("""
        <style>
        .timeline-container {
            position: relative;
            max-width: 1200px;
            margin: 0 auto;
        }
        .timeline-line {
            position: absolute;
            width: 2px;
            height: 100%;
            background: rgba(255,215,0,0.2);
            left: 50%;
            transform: translateX(-50%);
        }
        .timeline-event {
            position: relative;
            margin: 2rem 0;
            width: 100%;
            display: flex;
            justify-content: center;
            opacity: 0;
            animation: fadeIn 0.5s ease forwards;
        }
        .timeline-content {
            background: linear-gradient(145deg, rgba(49,51,63,0.1) 0%, rgba(49,51,63,0.05) 100%);
            border: 1px solid rgba(255,215,0,0.1);
            border-radius: 10px;
            padding: 1rem;
            width: 45%;
            position: relative;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .timeline-content:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.2);
        }
        .timeline-date {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 0.5rem;
        }
        .timeline-title {
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: rgba(255,215,0,0.8);
        }
        .timeline-description {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .timeline-icon {
            width: 40px;
            height: 40px;
            background: rgba(255,215,0,0.1);
            border-radius: 50%;
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255,215,0,0.2);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """, unsafe_allow_html=True)

        if not self.events:
            self.events = self.get_default_events()

        st.markdown("""
            <div class="timeline-container">
                <div class="timeline-line"></div>
        """, unsafe_allow_html=True)

        for idx, event in enumerate(self.events):
            align_left = idx % 2 == 0
            date_str = event["date"].strftime("%d %b, %Y")
            
            st.markdown(f"""
                <div class="timeline-event" style="animation-delay: {idx * 0.2}s;">
                    <div class="timeline-icon">
                        <i class="fas fa-{event['icon']}" style="color: rgba(255,215,0,0.8);"></i>
                    </div>
                    <div class="timeline-content" style="{'margin-right: 55%;' if align_left else 'margin-left: 55%;'}">
                        <div class="timeline-date">{date_str}</div>
                        <div class="timeline-title">{event['title']}</div>
                        <div class="timeline-description">{event['description']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

def render_investment_journey():
    """Función principal para mostrar la línea de tiempo de inversión"""
    st.title("Tu Viaje de Inversión")
    
    # Información general
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Días en el mercado", "30", "+2")
    with col2:
        st.metric("Objetivos completados", "3", "+1")
    with col3:
        st.metric("Nivel actual", "Intermedio", "⭐")

    # Mostrar línea de tiempo
    timeline = InvestmentTimeline()
    timeline.render_timeline()

    # Próximos objetivos
    st.subheader("Próximos Objetivos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style='
                padding: 1rem;
                background: rgba(49,51,63,0.1);
                border-radius: 10px;
                margin-bottom: 1rem;
            '>
                <h4>Diversificación Internacional</h4>
                <p>Invierte en al menos 3 mercados diferentes</p>
                <div style='
                    width: 70%;
                    height: 6px;
                    background: rgba(255,215,0,0.2);
                    border-radius: 3px;
                    margin-top: 0.5rem;
                '>
                    <div style='
                        width: 60%;
                        height: 100%;
                        background: rgba(255,215,0,0.8);
                        border-radius: 3px;
                    '></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style='
                padding: 1rem;
                background: rgba(49,51,63,0.1);
                border-radius: 10px;
                margin-bottom: 1rem;
            '>
                <h4>Estrategia Avanzada</h4>
                <p>Completa 5 análisis técnicos</p>
                <div style='
                    width: 70%;
                    height: 6px;
                    background: rgba(255,215,0,0.2);
                    border-radius: 3px;
                    margin-top: 0.5rem;
                '>
                    <div style='
                        width: 40%;
                        height: 100%;
                        background: rgba(255,215,0,0.8);
                        border-radius: 3px;
                    '></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
