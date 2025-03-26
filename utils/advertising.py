import streamlit as st
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta

class AdvertisementStats:
    def __init__(self):
        self.impressions = 0
        self.clicks = 0
        self.revenue = 0.0
        self.last_updated = datetime.now()
        self.click_history = []

class Advertisement:
    def __init__(self, id: str, title: str, description: str, 
                 link: str, image_url: Optional[str] = None,
                 category: str = "general", revenue_per_click: float = 0.0):
        self.id = id
        self.title = title
        self.description = description
        self.link = link
        self.image_url = image_url
        self.category = category
        self.revenue_per_click = revenue_per_click
        self.stats = AdvertisementStats()

class AdvertisingManager:
    def __init__(self):
        """
        Programas de afiliados reales y rentables:
        1. eToro Partners: https://www.etoropartners.com/
        2. Plus500 Affiliate: https://www.500affiliates.com/
        3. Trading 212 Affiliate: https://www.trading212.com/en/affiliate-program
        4. XM Partners: https://partners.xm.com/
        5. Admirals Partners: https://admiralpartners.com/
        """
        self.ads = {
            "broker": [
                Advertisement(
                    "broker1",
                    "Plus500 - Trading CFDs",
                    "Opere CFDs con una plataforma regulada. Más de 2000 instrumentos.",
                    "https://www.500affiliates.com/scripts/click.php?a_aid=YOUR_ID",
                    category="broker",
                    revenue_per_click=2.5  # Ejemplo: $2.5 por clic
                ),
                Advertisement(
                    "broker2",
                    "eToro - Social Trading",
                    "Copie a traders exitosos automáticamente. Comience con €50.",
                    "https://www.etoropartners.com/ref/?partner_id=YOUR_ID",
                    category="broker",
                    revenue_per_click=3.0  # Ejemplo: $3 por clic
                )
            ],
            "education": [
                Advertisement(
                    "edu1",
                    "XM Trading Academy",
                    "Cursos gratuitos de trading y seminarios en vivo",
                    "https://partners.xm.com/ref?id=YOUR_ID",
                    category="education",
                    revenue_per_click=1.5
                ),
                Advertisement(
                    "edu2",
                    "Admirals Forex Education",
                    "Webinars diarios y cursos certificados",
                    "https://admiralpartners.com/?ref=YOUR_ID",
                    category="education",
                    revenue_per_click=1.75
                )
            ],
            "tools": [
                Advertisement(
                    "tool1",
                    "TradingView Pro",
                    "Gráficos profesionales y alertas en tiempo real",
                    "https://www.tradingview.com/gopro/?share=YOUR_ID",
                    category="tools",
                    revenue_per_click=1.0
                )
            ]
        }

        if 'ad_stats' not in st.session_state:
            st.session_state.ad_stats = {}

    def track_impression(self, ad_id: str):
        """Registrar una impresión de anuncio"""
        if ad_id not in st.session_state.ad_stats:
            st.session_state.ad_stats[ad_id] = AdvertisementStats()
        st.session_state.ad_stats[ad_id].impressions += 1

    def track_click(self, ad_id: str):
        """Registrar un clic en un anuncio"""
        if ad_id not in st.session_state.ad_stats:
            st.session_state.ad_stats[ad_id] = AdvertisementStats()
        stats = st.session_state.ad_stats[ad_id]
        stats.clicks += 1
        stats.click_history.append(datetime.now())

        # Calcular ingresos estimados
        for category in self.ads.values():
            for ad in category:
                if ad.id == ad_id:
                    stats.revenue += ad.revenue_per_click
                    break

    def get_analytics(self) -> Dict:
        """Obtener análisis de rendimiento publicitario"""
        total_impressions = 0
        total_clicks = 0
        total_revenue = 0.0
        ctr = 0.0  # Click-through rate

        for stats in st.session_state.ad_stats.values():
            total_impressions += stats.impressions
            total_clicks += stats.clicks
            total_revenue += stats.revenue

        if total_impressions > 0:
            ctr = (total_clicks / total_impressions) * 100

        return {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_revenue": total_revenue,
            "ctr": ctr,
            "last_24h_clicks": self.get_clicks_last_24h()
        }

    def get_clicks_last_24h(self) -> int:
        """Obtener número de clics en las últimas 24 horas"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        total_clicks = 0

        for stats in st.session_state.ad_stats.values():
            recent_clicks = [click for click in stats.click_history 
                           if click > yesterday]
            total_clicks += len(recent_clicks)

        return total_clicks

    def render_analytics_dashboard(self):
        """Renderizar panel de control de análisis publicitario"""
        analytics = self.get_analytics()

        st.header("📊 Panel de Control Publicitario")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Impresiones Totales", f"{analytics['total_impressions']:,}")

        with col2:
            st.metric("Clics Totales", f"{analytics['total_clicks']:,}")

        with col3:
            st.metric("CTR", f"{analytics['ctr']:.2f}%")

        with col4:
            st.metric("Ingresos Estimados", f"${analytics['total_revenue']:,.2f}")

        # Gráfico de clics últimas 24h
        st.subheader("Actividad Reciente")
        st.metric("Clics (24h)", analytics['last_24h_clicks'])

    def render_sidebar_ad(self, category: str = "general"):
        """Renderizar un anuncio en la barra lateral"""
        ad = self.get_ad(category)
        if ad:
            self.track_impression(ad.id)
            st.sidebar.markdown("---")
            st.sidebar.markdown("### Patrocinado")
            with st.sidebar.container():
                st.markdown(f"""
                <div style='
                    padding: 1rem;
                    background: rgba(255,215,0,0.1);
                    border-radius: 10px;
                    margin: 1rem 0;
                '>
                    <h4>{ad.title}</h4>
                    <p>{ad.description}</p>
                    <a href="{ad.link}" target="_blank" 
                       onclick="trackClick('{ad.id}')" 
                       style="color: #FFD700;">
                        Saber más →
                    </a>
                </div>
                """, unsafe_allow_html=True)

            # JavaScript para tracking de clics
            st.markdown(f"""
                <script>
                function trackClick(adId) {{
                    fetch('/track_click', {{
                        method: 'POST',
                        body: JSON.stringify({{ ad_id: adId }}),
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                }}
                </script>
            """, unsafe_allow_html=True)

    def get_ad(self, category: str = "general") -> Optional[Advertisement]:
        """Obtener un anuncio aleatorio de una categoría específica"""
        if category in self.ads and self.ads[category]:
            return random.choice(self.ads[category])
        return None

    def render_inline_ad(self, category: str = "general"):
        """Renderizar un anuncio en línea dentro del contenido"""
        ad = self.get_ad(category)
        if ad:
            self.track_impression(ad.id)
            with st.container():
                st.markdown(f"""
                <div style='
                    padding: 1rem;
                    background: rgba(255,215,0,0.05);
                    border-radius: 10px;
                    margin: 1rem 0;
                    border: 1px solid rgba(255,215,0,0.2);
                '>
                    <small style='opacity: 0.7;'>Contenido Patrocinado</small>
                    <h4>{ad.title}</h4>
                    <p>{ad.description}</p>
                    <a href="{ad.link}" target="_blank" onclick="trackClick('{ad.id}')" style="color: #FFD700;">
                        Más información →
                    </a>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
                <script>
                function trackClick(adId) {{
                    fetch('/track_click', {{
                        method: 'POST',
                        body: JSON.stringify({{ ad_id: adId }}),
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                }}
                </script>
            """, unsafe_allow_html=True)


    def render_banner_ad(self, category: str = "general"):
        """Renderizar un banner publicitario"""
        ad = self.get_ad(category)
        if ad:
            self.track_impression(ad.id)
            st.markdown(f"""
            <div style='
                width: 100%;
                padding: 0.5rem;
                background: linear-gradient(90deg, rgba(255,215,0,0.1) 0%, rgba(255,215,0,0.05) 100%);
                border-radius: 5px;
                margin: 0.5rem 0;
                text-align: center;
            '>
                <a href="{ad.link}" target="_blank" onclick="trackClick('{ad.id}')" style="
                    color: #FFD700;
                    text-decoration: none;
                    font-size: 0.9rem;
                ">
                    {ad.title} - {ad.description} →
                </a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <script>
                function trackClick(adId) {{
                    fetch('/track_click', {{
                        method: 'POST',
                        body: JSON.stringify({{ ad_id: adId }}),
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                }}
                </script>
            """, unsafe_allow_html=True)