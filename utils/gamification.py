import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class Achievement:
    def __init__(self, id: str, name: str, description: str, points: int, icon: str):
        self.id = id
        self.name = name
        self.description = description
        self.points = points
        self.icon = icon
        self.completed = False
        self.completed_date = None

class Challenge:
    def __init__(self, id: str, name: str, description: str, points: int, 
                 duration_days: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.points = points
        self.duration_days = duration_days
        self.completed = False
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=duration_days)

class GamificationSystem:
    def __init__(self):
        if 'user_points' not in st.session_state:
            st.session_state.user_points = 0
        if 'user_level' not in st.session_state:
            st.session_state.user_level = 1
        if 'achievements' not in st.session_state:
            st.session_state.achievements = self._initialize_achievements()
        if 'daily_challenges' not in st.session_state:
            st.session_state.daily_challenges = self._generate_daily_challenges()
            
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Inicializar logros disponibles"""
        achievements = {
            "first_trade": Achievement(
                "first_trade",
                "🎯 Primer Operación",
                "Realiza tu primera operación en el mercado",
                100,
                "🎯"
            ),
            "portfolio_diversity": Achievement(
                "portfolio_diversity",
                "🌈 Diversificador",
                "Ten acciones de al menos 5 sectores diferentes",
                200,
                "🌈"
            ),
            "profit_master": Achievement(
                "profit_master",
                "💰 Maestro del Beneficio",
                "Obtén un rendimiento total del 20% en tu portafolio",
                500,
                "💰"
            ),
            "news_analyst": Achievement(
                "news_analyst",
                "📰 Analista de Noticias",
                "Lee 50 noticias financieras",
                150,
                "📰"
            ),
            "alert_expert": Achievement(
                "alert_expert",
                "🔔 Experto en Alertas",
                "Configura 10 alertas de precio",
                200,
                "🔔"
            )
        }
        return achievements

    def _generate_daily_challenges(self) -> List[Challenge]:
        """Generar desafíos diarios"""
        challenges = [
            Challenge(
                "daily_research",
                "📚 Investigador Diario",
                "Lee 5 noticias financieras hoy",
                50,
                1
            ),
            Challenge(
                "market_analysis",
                "📊 Analista de Mercado",
                "Revisa el rendimiento de 3 sectores diferentes",
                75,
                1
            ),
            Challenge(
                "portfolio_check",
                "💼 Revision de Cartera",
                "Actualiza tu cartera de inversión",
                60,
                1
            )
        ]
        return challenges

    def award_points(self, points: int, reason: str):
        """Otorgar puntos al usuario"""
        st.session_state.user_points += points
        self._check_level_up()
        st.success(f"¡Has ganado {points} puntos por {reason}! 🎉")

    def _check_level_up(self):
        """Verificar si el usuario sube de nivel"""
        points_per_level = 1000
        new_level = (st.session_state.user_points // points_per_level) + 1
        
        if new_level > st.session_state.user_level:
            st.session_state.user_level = new_level
            st.balloons()
            st.success(f"¡Has alcanzado el nivel {new_level}! 🎊")

    def complete_achievement(self, achievement_id: str):
        """Marcar un logro como completado"""
        if achievement_id in st.session_state.achievements:
            achievement = st.session_state.achievements[achievement_id]
            if not achievement.completed:
                achievement.completed = True
                achievement.completed_date = datetime.now()
                self.award_points(achievement.points, f"completar el logro: {achievement.name}")

    def complete_challenge(self, challenge_id: str):
        """Marcar un desafío como completado"""
        for challenge in st.session_state.daily_challenges:
            if challenge.id == challenge_id and not challenge.completed:
                challenge.completed = True
                self.award_points(challenge.points, f"completar el desafío: {challenge.name}")

    def get_user_progress(self) -> Dict:
        """Obtener progreso del usuario"""
        return {
            "points": st.session_state.user_points,
            "level": st.session_state.user_level,
            "achievements": st.session_state.achievements,
            "daily_challenges": st.session_state.daily_challenges
        }

def render_gamification_ui():
    """Renderizar interfaz de gamificación"""
    gamification = GamificationSystem()
    progress = gamification.get_user_progress()

    st.header("🎮 Tu Progreso de Inversión")

    # Showcase de Logros Destacados
    st.subheader("🏆 Logros Destacados")
    achievement_cols = st.columns(3)

    # Filtrar logros completados para el showcase
    completed_achievements = [
        achievement for achievement in progress['achievements'].values()
        if achievement.completed
    ]

    # Mostrar últimos 3 logros completados
    for idx, col in enumerate(achievement_cols):
        with col:
            st.markdown("""
                <div style='padding: 1rem; 
                          background: rgba(255,215,0,0.1); 
                          border-radius: 10px;
                          text-align: center;'>
            """, unsafe_allow_html=True)

            if idx < len(completed_achievements):
                achievement = completed_achievements[idx]
                st.markdown(f"""
                    <h3 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>{achievement.icon}</h3>
                    <h4>{achievement.name}</h4>
                    <p style='font-size: 0.9rem; opacity: 0.8;'>{achievement.description}</p>
                    <p style='color: gold;'>+{achievement.points} puntos</p>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <h3 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🔒</h3>
                    <h4>Próximo Logro</h4>
                    <p style='font-size: 0.9rem; opacity: 0.8;'>¡Completa más desafíos para desbloquear!</p>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # Mostrar nivel y puntos
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nivel de Inversor", f"{progress['level']} 🏆")
    with col2:
        st.metric("Puntos de Experiencia", f"{progress['points']} ⭐")

    # Barra de progreso al siguiente nivel
    points_per_level = 1000
    current_level_points = progress['points'] % points_per_level
    progress_percentage = (current_level_points / points_per_level) * 100

    st.markdown(f"""
        <div style='margin: 1rem 0;'>
            <p>Progreso al siguiente nivel:</p>
            <div style='
                background: rgba(255,215,0,0.1);
                border-radius: 10px;
                height: 20px;
                overflow: hidden;
            '>
                <div style='
                    width: {progress_percentage}%;
                    background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
                    height: 100%;
                    transition: width 0.5s ease;
                '></div>
            </div>
            <p style='text-align: right; font-size: 0.9rem;'>
                {current_level_points}/{points_per_level} puntos
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Mostrar desafíos diarios
    st.subheader("📅 Desafíos Diarios")
    for challenge in progress['daily_challenges']:
        with st.expander(f"{challenge.icon if hasattr(challenge, 'icon') else '🎯'} {challenge.name}", expanded=not challenge.completed):
            st.write(challenge.description)
            st.write(f"Recompensa: {challenge.points} puntos")
            if not challenge.completed:
                if st.button("✅ Completar", key=f"challenge_{challenge.id}"):
                    gamification.complete_challenge(challenge.id)
                    st.rerun()
            else:
                st.success("¡Completado! 🎉")

    # Mostrar todos los logros
    st.subheader("🏆 Todos los Logros")
    achievements_list = list(progress['achievements'].values())
    for i in range(0, len(achievements_list), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(achievements_list):
                achievement = achievements_list[i + j]
                with cols[j]:
                    with st.container():
                        st.markdown(f"""
                        <div style='padding: 1rem; background: rgba(255,215,0,0.1); border-radius: 10px;'>
                            <h4>{achievement.icon} {achievement.name}</h4>
                            <p>{achievement.description}</p>
                            <p><strong>Puntos:</strong> {achievement.points}</p>
                            <p><strong>Estado:</strong> {'✅ Completado' if achievement.completed else '⏳ Pendiente'}</p>
                        </div>
                        """, unsafe_allow_html=True)