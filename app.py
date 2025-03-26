import streamlit as st
import pandas as pd
from utils.portfolio import Portfolio
from utils.market_data import MarketData
from utils.ai_advisor import AIAdvisor
from utils.news import NewsService
from utils.report_generator import ReportGenerator
from utils.recommendation_engine import RecommendationEngine
from utils.alert_manager import AlertManager
from utils.data_aggregator import DataAggregator
from utils.advertising import AdvertisingManager
from utils.gamification import render_gamification_ui
from utils.broker_integration import PortfolioAggregator, BrokerConnection # Added BrokerConnection import
from utils.broker_compatibility import BrokerCompatibility
from utils.risk_profiler import RiskProfiler
from utils.timeline import render_investment_journey
from utils.auth import AuthManager, require_auth
from utils.monetization import MonetizationManager
from utils.launch_manager import LaunchManager
from utils.loading_screen import render_loading_screen, show_loading_overlay, remove_loading_overlay
from utils.feedback import FeedbackManager
from utils.donations import DonationManager
from datetime import datetime

# Page config
st.set_page_config(
    page_title="BROKER.IA",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Show loading screen while initializing
show_loading_overlay()

# Initialize session state and managers
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()
if 'portfolios' not in st.session_state:
    if st.session_state.auth_manager.is_authenticated():
        user = st.session_state.auth_manager.get_current_user()
        st.session_state.portfolios = Portfolio.load_user_portfolios(user['id'])
    else:
        st.session_state.portfolios = {}
if 'current_report' not in st.session_state:
    st.session_state.current_report = None
if 'alert_manager' not in st.session_state:
    st.session_state.alert_manager = AlertManager()
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'ad_manager' not in st.session_state:
    st.session_state.ad_manager = AdvertisingManager()
if 'portfolio_aggregator' not in st.session_state:
    st.session_state.portfolio_aggregator = PortfolioAggregator()
if 'risk_profile' not in st.session_state:
    st.session_state.risk_profile = None
if 'monetization_manager' not in st.session_state:
    st.session_state.monetization_manager = MonetizationManager()
if 'launch_manager' not in st.session_state:
    st.session_state.launch_manager = LaunchManager()
if 'feedback_manager' not in st.session_state:
    st.session_state.feedback_manager = FeedbackManager()
if 'donation_manager' not in st.session_state:
    st.session_state.donation_manager = DonationManager()

# Remove loading overlay after initialization
remove_loading_overlay()


def main():
    # Logo y título en la barra lateral
    st.sidebar.image("attached_assets/Broker_IA_transparent.png", width=200)
    st.sidebar.markdown("---")

    # Verificar si el usuario es administrador
    is_admin = False
    if st.session_state.auth_manager.is_authenticated():
        is_admin = st.session_state.auth_manager.is_admin()

    # Renderizar UI de autenticación o lista de espera
    if not st.session_state.auth_manager.is_authenticated():
        st.session_state.auth_manager.render_login_ui()
    elif not is_admin:  # Si no es admin, verificar acceso
        user = st.session_state.auth_manager.get_current_user()
        if not st.session_state.launch_manager.check_access_allowed(user['id']):
            st.warning("Tu acceso está pendiente de aprobación.")
            st.session_state.launch_manager.render_waitlist_ui()
    else:
        if is_admin:
            show_authenticated_content()
        else:
            # Verificar acceso permitido
            user = st.session_state.auth_manager.get_current_user()
            if st.session_state.launch_manager.check_access_allowed(user['id']):
                show_authenticated_content()
            else:
                st.warning("Tu acceso está pendiente de aprobación.")
                st.session_state.launch_manager.render_waitlist_ui()

@require_auth
def show_authenticated_content():
    """Mostrar contenido para usuarios autenticados"""
    # Verificar acceso de administrador
    is_admin = st.session_state.auth_manager.is_admin()

    # Panel de control de lanzamiento solo para admin
    if is_admin:
        st.session_state.launch_manager.render_admin_launch_control()
        st.markdown("---")

    # Navegación mejorada
    pages = {
        "Dashboard": "Panel Principal",
        "Perfil de Riesgo": "Perfil de Riesgo",
        "Gestión de Carteras": "Gestión de Carteras",
        "Noticias del Mercado": "Noticias del Mercado",
        "Asesor AI": "Asesor IA",
        "Informes": "Informes",
        "Recomendaciones": "Recomendaciones",
        "Alertas": "Sistema de Alertas",
        "Progreso": "Progreso",
        "Membresía": "Membresía",
        "Feedback": "Feedback y Sugerencias",
        "Donaciones": "Apoyar el Proyecto"
    }

    # Si es administrador, mostrar panel de administración
    if is_admin:
        st.sidebar.markdown("### Panel de Administración")
        compatibility_checker = BrokerCompatibility()
        compatibility_checker.render_compatibility_ui()
        st.session_state.monetization_manager.render_admin_metrics()  # Nuevas métricas
        st.markdown("---")

    # Navegación principal
    for page_name, display_name in pages.items():
        clicked = st.sidebar.button(
            display_name,
            key=f"nav_{page_name}",
            use_container_width=True,
            help=f"Ir a {display_name}"
        )
        if clicked:
            st.session_state.page = page_name
            st.rerun()

    # Mostrar anuncio en la barra lateral
    st.session_state.ad_manager.render_sidebar_ad()

    # Contenido principal
    if st.session_state.page == "Perfil de Riesgo":
        show_risk_profile()
    elif st.session_state.page == "Dashboard":
        show_dashboard()
    elif st.session_state.page == "Gestión de Carteras":
        show_portfolio_management()
    elif st.session_state.page == "Noticias del Mercado":
        show_market_news()
    elif st.session_state.page == "Asesor AI":
        show_ai_advisor()
    elif st.session_state.page == "Informes":
        show_reports()
    elif st.session_state.page == "Recomendaciones":
        show_recommendations()
    elif st.session_state.page == "Alertas":
        show_alerts()
    elif st.session_state.page == "Progreso":
        show_progress()
    elif st.session_state.page == "Membresía":
        show_membership()
    elif st.session_state.page == "Feedback":
        st.session_state.feedback_manager.render_feedback_ui()
    elif st.session_state.page == "Donaciones":
        st.session_state.donation_manager.render_donation_ui()


def show_dashboard():
    # Crear un layout de tarjetas para información importante
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div style='padding: 1rem; background: rgba(255,215,0,0.1); border-radius: 10px;'>
                <h3>💰 Valor Total</h3>
            </div>
        """, unsafe_allow_html=True)
        if st.session_state.portfolios:
            total_value = sum(portfolio.get_total_value()
                            for portfolio in st.session_state.portfolios.values())
            st.metric("", f"${total_value:,.2f}")
        else:
            if st.button("Crear Primera Cartera", key="create_first_portfolio"):
                st.session_state.page = "Gestión de Carteras"
                st.rerun()

    with col2:
        st.markdown("""
            <div style='padding: 1rem; background: rgba(255,215,0,0.1); border-radius: 10px;'>
                <h3>📈 Rendimiento</h3>
            </div>
        """, unsafe_allow_html=True)
        market_data = MarketData()
        sp500_return = market_data.get_market_return()
        st.metric("", f"{sp500_return:.2f}%",
                 delta=f"{sp500_return:.2f}%",
                 delta_color='normal' if sp500_return > 0 else 'inverse')
        if st.button("Ver Más Noticias", key="see_more_news"):
            st.session_state.page = "Noticias del Mercado"
            st.rerun()

    with col3:
        st.markdown("""
            <div style='padding: 1rem; background: rgba(255,215,0,0.1); border-radius: 10px;'>
                <h3>🎯 Objetivos</h3>
            </div>
        """, unsafe_allow_html=True)
        if st.session_state.portfolios:
            completed_goals = len([p for p in st.session_state.portfolios.values()
                                 if p.get_total_value() > 0])
            st.metric("", f"{completed_goals} completados")
            if st.button("Ver Progreso", key="see_progress"):
                st.session_state.page = "Progreso"
                st.rerun()
        else:
            st.info("Define tus objetivos")
            if st.button("Configurar Objetivos", key="set_goals"):
                st.session_state.page = "Progreso"
                st.rerun()

    # Separador visual
    st.markdown("---")

    # Sección de rendimiento de carteras
    if st.session_state.portfolios:
        st.subheader("📊 Rendimiento de Carteras")
        tabs = st.tabs([f"📈 {name}" for name in st.session_state.portfolios.keys()])

        for tab, (name, portfolio) in zip(tabs, st.session_state.portfolios.items()):
            with tab:
                performance_data = portfolio.get_performance_history()
                st.plotly_chart(portfolio.create_performance_chart(performance_data),
                              use_container_width=True)
                if st.button("Gestionar Cartera", key=f"manage_{name}"):
                    st.session_state.page = "Gestión de Carteras"
                    st.rerun()
    else:
        st.info("🚀 ¡Comienza tu viaje de inversión! Crea tu primera cartera en la sección 'Gestión de Carteras'.")
        if st.button("Comenzar Ahora", key="start_investing"):
            st.session_state.page = "Gestión de Carteras"
            st.rerun()


def show_portfolio_management():
    st.header("Gestión de Carteras")

    # Crear pestañas para separar la gestión manual de la integración con brokers
    tabs = st.tabs(["Carteras Conectadas", "Gestión Manual", "Conectar Broker"])

    with tabs[0]:
        st.session_state.portfolio_aggregator.render_connected_portfolios()

    with tabs[1]:
        st.session_state.portfolio_aggregator.render_manual_import_guide()
        with st.expander("Añadir Nueva Cartera", expanded=True):
            portfolio_name = st.text_input("Nombre de la Cartera", key="portfolio_name_input")

            # Opciones para añadir cartera
            add_method = st.radio(
                "Método de añadir acciones",
                ["Manualmente", "Importar archivo"],
                key="add_method"
            )

            if add_method == "Manualmente":
                symbol = st.text_input("Símbolo de la acción (ej: AAPL)", key="manual_symbol").upper()
                shares = st.number_input("Número de acciones", min_value=0.0, step=0.01, key="manual_shares")

                if st.button("Añadir Acción", key="add_action_button"):
                    if portfolio_name:
                        try:
                            # Crear o obtener la cartera
                            if portfolio_name not in st.session_state.portfolios:
                                user = st.session_state.auth_manager.get_current_user()
                                portfolio = Portfolio(portfolio_name, user['id'])
                                portfolio.save()  # Guardar la cartera primero
                                # Recargar todas las carteras del usuario
                                st.session_state.portfolios = Portfolio.load_user_portfolios(user['id'])

                            if symbol and shares > 0:
                                st.session_state.portfolios[portfolio_name].add_position(symbol, shares)
                                st.session_state.portfolios[portfolio_name].save()
                                # Recargar las carteras después de añadir la posición
                                user = st.session_state.auth_manager.get_current_user()
                                st.session_state.portfolios = Portfolio.load_user_portfolios(user['id'])
                                st.success(f"¡Cartera '{portfolio_name}' creada y acción {symbol} añadida correctamente!")
                                st.rerun()
                            else:
                                st.warning("Por favor, introduce un símbolo y número de acciones válido.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    else:
                        st.warning("Por favor, introduce un nombre para la cartera.")

            else:  # Importar archivo
                portfolio_file = st.file_uploader("Subir archivo de cartera (CSV/Excel)", type=['csv', 'xlsx'], key="portfolio_file_upload")

                if st.button("Importar Cartera", key="import_portfolio_button_1"):
                    if portfolio_name and portfolio_name not in st.session_state.portfolios:
                        if portfolio_file:
                            broker = BrokerConnection("Manual Import", "user_id")
                            if broker.connect_with_file(portfolio_file):
                                portfolio = Portfolio(portfolio_name)
                                positions = broker.positions
                                for position in positions:
                                    try:
                                        portfolio.add_position(position['symbol'], float(position['shares']))
                                    except Exception as e:
                                        st.warning(f"No se pudo importar {position['symbol']}: {str(e)}")
                                st.session_state.portfolios[portfolio_name] = portfolio
                                st.success(f"¡Cartera '{portfolio_name}' importada correctamente!")
                                st.rerun()
                        else:
                            st.warning("Por favor, selecciona un archivo para importar.")
                    else:
                        st.warning("Por favor, introduce un nombre único para la cartera.")


    with tabs[2]:
        st.info("La conexión directa con brokers no está disponible en este momento. Por favor, utiliza la opción de importación manual de carteras.")


def show_market_news():
    st.header("Noticias del Mercado")

    # Mostrar anuncio de educación
    st.session_state.ad_manager.render_inline_ad("education")

    # Inicializar servicios
    data_aggregator = DataAggregator()

    # Mostrar indicador de carga
    with st.spinner():
        render_loading_screen("Cargando noticias del mercado")
        try:
            # Obtener noticias de múltiples fuentes
            news = data_aggregator.get_financial_news(days=7)
            market_data = data_aggregator.get_market_movers()
            sector_data = data_aggregator.get_sector_performance()

            # Mostrar datos del mercado
            st.subheader("📊 Visión General del Mercado")
            market_cols = st.columns(3)

            for idx, (index, data) in enumerate(market_data.items()):
                with market_cols[idx]:
                    delta_color = 'normal' if data['change'] > 0 else 'inverse'
                    st.metric(
                        data['name'],
                        f"${data['price']:,.2f}",
                        f"{data['change']:+.2f}%",
                        delta_color=delta_color
                    )

            # Mostrar rendimiento sectorial
            st.subheader("🏢 Rendimiento por Sector")
            sector_cols = st.columns(4)
            for idx, (sector, data) in enumerate(sector_data.items()):
                with sector_cols[idx % 4]:
                    delta_color = 'normal' if data['change'] > 0 else 'inverse'
                    st.metric(
                        data['name'],
                        f"{data['change']:+.2f}%",
                        delta_color=delta_color
                    )

            # Filtros y actualización de noticias
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption("Las noticias se actualizan automáticamente cada 5 minutos")
            with col2:
                if st.button("🔄 Actualizar Noticias", key="update_news_button"):
                    st.cache_data.clear()
                    st.rerun()

            # Mostrar noticias
            st.subheader("📰 Últimas Noticias")
            for article in news:
                with st.expander(f"📄 {article['title']}", expanded=True):
                    st.markdown(f"""
                    **Fuente:** {article['source']}  
                    **Fecha:** {article['publishedAt']}

                    {article['description']}
                    """)

                    if article.get('urlToImage'):
                        st.image(article['urlToImage'], caption=article['source'])

                    st.markdown(f"[🔗 Leer más]({article['url']})")

        except Exception as e:
            st.error(f"Error al cargar los datos: {str(e)}")
            st.button("🔄 Reintentar", on_click=lambda: st.rerun(), key="retry_news_button")


def show_ai_advisor():
    st.header("Asesor Financiero AI")

    # Mostrar anuncio de herramientas
    st.session_state.ad_manager.render_inline_ad("tools")

    st.write("""
    💡 Tu asesor financiero personal, potenciado por IA.
    Pregunta cualquier cosa sobre:
    - Análisis de mercado en tiempo real
    - Estrategias de inversión
    - Gestión de carteras
    - Interpretación de noticias financieras
    """)

    question = st.text_area("Haz tu pregunta financiera:")
    if st.button("Obtener Asesoramiento", key="get_advice_button"):
        if question:
            advisor = AIAdvisor()
            with st.spinner():
                render_loading_screen("Analizando tu pregunta")
                try:
                    response = advisor.get_advice(question)
                    st.write(response)
                except Exception as e:
                    st.error(f"Error al obtener asesoramiento: {str(e)}")
        else:
            st.warning("Por favor, introduce una pregunta.")


def show_reports():
    st.header("Generador de Informes de Inversión")

    if not st.session_state.portfolios:
        st.warning("Necesitas crear al menos un portafolio para generar informes.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_portfolio = st.selectbox(
            "Seleccionar Portafolio",
            list(st.session_state.portfolios.keys())
        )

    with col2:
        if st.button("🔄 Generar Informe", key="generate_report_button"):
            with st.spinner("Generando informe personalizado..."):
                report_generator = ReportGenerator()
                portfolio = st.session_state.portfolios[selected_portfolio]
                st.session_state.current_report = report_generator.generate_complete_report(portfolio)

    if st.session_state.current_report:
        report = st.session_state.current_report

        # Mostrar fecha del informe
        st.caption(f"Generado el: {report['date']}")

        # Análisis del Portafolio
        with st.expander("📊 Análisis del Portafolio", expanded=True):
            st.markdown(report['portfolio_analysis'])

        # Análisis del Mercado
        with st.expander("📈 Análisis del Mercado", expanded=True):
            st.markdown(report['market_analysis'])

        # Recomendaciones de IA
        with st.expander("🤖 Recomendaciones de IA", expanded=True):
            st.markdown(report['ai_recommendations'])

        # Opciones de exportación (futura implementación)
        st.download_button(
            label="📥 Descargar Informe (PDF)",
            data="Función en desarrollo",
            file_name=f"informe_{selected_portfolio}_{report['date']}.pdf",
            mime="application/pdf",
            disabled=True
        )


def show_recommendations():
    st.header("Recomendaciones Automáticas de Inversión")

    if not st.session_state.portfolios:
        st.warning("Necesitas crear al menos un portafolio para recibir recomendaciones.")
        return

    if not st.session_state.risk_profile:
        st.warning("""
        Para obtener recomendaciones más precisas, completa primero tu perfil de riesgo.
        """)
        if st.button("Completar Perfil de Riesgo", key="complete_risk_profile_button"):
            st.session_state.page = "Perfil de Riesgo"
            st.rerun()
        st.markdown("---")

    # Selección de portafolio
    selected_portfolio = st.selectbox(
        "Seleccionar Portafolio",
        list(st.session_state.portfolios.keys())
    )

    portfolio = st.session_state.portfolios[selected_portfolio]

    # Botón para generar recomendaciones
    if st.button("Analizar Portafolio", key="analyze_portfolio_button"):
        with st.spinner("Analizando portafolio y condiciones de mercado..."):
            recommendation_engine = RecommendationEngine()
            recommendations = recommendation_engine.get_portfolio_recommendations(portfolio)

            # Mostrar análisis de riesgo
            st.subheader("Análisis de Riesgo")
            risk_cols = st.columns(3)

            with risk_cols[0]:
                st.metric("Nivel de Riesgo", recommendations['risk_analysis']['risk_level'])

            with risk_cols[1]:
                st.metric("Score de Diversificación",
                         f"{recommendations['risk_analysis']['diversification_score']}/100")

            with risk_cols[2]:
                st.metric("Riesgo de Concentración",
                         recommendations['risk_analysis']['concentration_risk'])

            # Mostrar análisis de mercado
            st.subheader("Análisis Detallado del Mercado")
            with st.expander("📊 Ver Análisis Completo", expanded=True):
                st.markdown("""
                <style>
                .market-analysis {
                    padding: 1rem;
                    background: rgba(49,51,63,0.1);
                    border-radius: 10px;
                    margin: 1rem 0;
                }
                </style>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="market-analysis">
                {recommendations['market_analysis']}
                </div>
                """, unsafe_allow_html=True)

            # Mostrar recomendaciones personalizadas
            st.subheader("Recomendaciones Personalizadas")
            with st.expander("🎯 Ver Recomendaciones Detalladas", expanded=True):
                if 'error' in recommendations['personalized_recommendations']:
                    st.error(recommendations['personalized_recommendations']['error'])
                else:
                    st.markdown(f"""
                    <div class="market-analysis">
                    {recommendations['personalized_recommendations']['ai_recommendations']}
                    </div>
                    """, unsafe_allow_html=True)

            # Mostrar recomendaciones de trading
            st.subheader("Señales de Trading")
            for rec in recommendations['trade_recommendations']:
                with st.expander(
                    f"{'📈' if rec['type'] == 'BUY' else '📉'} {rec['symbol']} - {rec['type']}",
                    expanded=True
                ):
                    st.markdown(f"""
                    <div class="market-analysis">
                    <h4>{rec['type']} - {rec['symbol']}</h4>
                    <p><strong>Razón:</strong> {rec['reason']}</p>
                    """, unsafe_allow_html=True)

                    if 'metrics' in rec:
                        st.markdown("<h4>Métricas Relevantes:</h4>", unsafe_allow_html=True)
                        for key, value in rec['metrics'].items():
                            st.markdown(f"- **{key}:** {value}")

                    st.markdown("</div>", unsafe_allow_html=True)

            # Timestamp y botón de descarga
            col1, col2 = st.columns([3,1])
            with col1:
                st.caption(f"Análisis actualizado: {recommendations['timestamp']}")
            with col2:
                st.download_button(
                    "📥 Descargar Análisis",
                    data=str(recommendations),
                    file_name=f"analisis_{selected_portfolio}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )


def show_alerts():
    st.header("🔔 Sistema de Alertas")

    # Crear nueva alerta
    with st.expander("➕ Crear Nueva Alerta", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            symbol = st.text_input("Símbolo de la Acción").upper()
            alert_type = st.selectbox(
                "Tipo de Alerta",
                ["precio", "volumen", "indicador técnico"]
            )

        with col2:
            condition = st.selectbox(
                "Condición",
                ["above", "below"],
                format_func=lambda x: "Mayor que" if x == "above" else "Menor que"
            )
            target_value = st.number_input("Valor Objetivo", min_value=0.0)

        email = st.text_input("Email para Notificaciones (opcional)")

        if st.button("Crear Alerta", key="create_alert_button"):
            if symbol and target_value > 0:
                alert_id = st.session_state.alert_manager.add_alert(
                    symbol, alert_type, condition, target_value, email
                )
                st.success(f"¡Alerta creada! ID: {alert_id}")

    # Mostrar alertas existentes
    st.subheader("📋 Alertas Activas")
    alerts = st.session_state.alert_manager.get_alerts()

    if not alerts:
        st.info("No hay alertas configuradas.")
    else:
        # Usar columnas para organizar las alertas
        for i in range(0, len(alerts), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(alerts):
                    alert = alerts[i + j]
                    with cols[j]:
                        with st.container():
                            st.markdown(f"""
                            #### {'🔔' if not alert.triggered else '✅'} {alert.symbol}
                            - **Tipo:** {alert.alert_type}
                            - **Condición:** {'>' if alert.condition == 'above' else '<'} {alert.target_value}
                            - **Estado:** {'Activada' if alert.triggered else 'Pendiente'}
                            - **Creada:** {alert.created_at.strftime('%Y-%m-%d %H:%M')}
                            """)

                            if not alert.triggered:
                                # Usar key única para cada botón
                                delete_key = f"delete_{alert.id}_{i}_{j}"
                                if st.button("🗑️ Eliminar", key=delete_key):
                                    st.session_state.alert_manager.remove_alert(alert.id)
                                    st.rerun()

    # Información sobre actualizaciones
    st.markdown("---")
    st.caption("💡 Las alertas se verifican automáticamente cada 5 minutos")


def show_progress():
    """Mostrar el progreso y la línea de tiempo del usuario"""
    render_investment_journey()


def show_risk_profile():
    risk_profiler = RiskProfiler()

    # Si ya tenemos un perfil calculado, mostrar un resumen
    if st.session_state.risk_profile:
        st.sidebar.success(f"Perfil actual: {st.session_state.risk_profile['profile']}")
        if st.sidebar.button("Realizar nuevo test", key="new_risk_test_button"):
            st.session_state.risk_profile = None
            st.rerun()

    # Mostrar el cuestionario
    profile_result = risk_profiler.render_quiz()

    if profile_result:
        st.session_state.risk_profile = profile_result


def show_membership(): # New function for membership page
    st.session_state.monetization_manager.render_membership_ui()


def custom_css():
    st.markdown("""
        <style>
        /* Animaciones y transiciones */
        .stButton > button {
            transition: all 0.3s ease;
            border-radius: 10px;
            border: 1px solid rgba(255, 215, 0, 0.2);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
        }

        /* Mejoras visuales */
        .main > div:first-child {
            padding-top: 0rem;
        }
        .stImage {
            margin-bottom: 2rem;
        }

        /* Personalización de la barra lateral */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #1E2126 0%, #0E1117 100%);
            padding-top: 2rem;
        }

        /* Estilos para navegación */
        [data-testid="stSidebar"] [data-testid="stButton"] {
            width: 100%;
            text-align: left;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            border-radius: 10px;
            background-color: transparent;
            border: none;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"]:hover {
            background-color: rgba(255, 215, 0, 0.1);
            transform: translateX(5px);
        }
        [data-testid="stSidebar"] [data-testid="stButton"].active {
            background-color: rgba(255, 215, 0, 0.2);
            border-left: 3px solid #FFD700;
        }

        /* Efectos para cards */
        div[data-testid="stVerticalBlock"] > div {
            transition: all 0.3s ease;
            border-radius: 10px;
            padding: 1rem;
        }
        div[data-testid="stVerticalBlock"] > div:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        /* Animaciones para métricas */
        .stMetric {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Estilo para el logo */
        [data-testid="stImage"] {
            background: transparent !important;
        }
        [data-testid="stImage"] img {
            max-width: 200px;
            margin: 0 auto;
            display: block;
            filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.2));
        }
        </style>
    """, unsafe_allow_html=True)

custom_css()

if __name__ == "__main__":
    main()