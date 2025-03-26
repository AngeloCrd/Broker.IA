import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
import os
import pandas as pd

class MonetizationManager:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.membership_plans = {
            "basic": {
                "name": "Plan Básico",
                "price": 0,
                "features": [
                    "Análisis básico de mercado",
                    "1 portafolio",
                    "Alertas básicas"
                ]
            },
            "pro": {
                "name": "Plan Pro",
                "price": 29.99,
                "features": [
                    "Análisis avanzado de mercado",
                    "Portafolios ilimitados",
                    "Alertas avanzadas",
                    "Recomendaciones personalizadas",
                    "Sin anuncios"
                ]
            },
            "enterprise": {
                "name": "Plan Enterprise",
                "price": 99.99,
                "features": [
                    "Todo lo incluido en Pro",
                    "API access",
                    "Soporte prioritario",
                    "Reportes personalizados",
                    "Análisis predictivo avanzado"
                ]
            }
        }

    def track_conversion(self, user_id: int, event_type: str, value: float, source: str, metadata: Dict = None):
        """Registrar una conversión"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO conversions (user_id, event_type, value, source, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, event_type, value, source, json.dumps(metadata or {})))
                self.conn.commit()
            return True
        except Exception as e:
            st.error(f"Error tracking conversion: {str(e)}")
            return False

    def get_user_membership(self, user_id: int) -> Dict:
        """Obtener membresía actual del usuario"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT plan_type, start_date, end_date, status
                    FROM memberships
                    WHERE user_id = %s AND status = 'active'
                    ORDER BY start_date DESC
                    LIMIT 1
                """, (user_id,))
                membership = cur.fetchone()

                if membership:
                    return {
                        "plan": membership[0],
                        "start_date": membership[1],
                        "end_date": membership[2],
                        "status": membership[3],
                        "features": self.membership_plans[membership[0]]["features"]
                    }
                return {"plan": "basic", "features": self.membership_plans["basic"]["features"]}
        except Exception as e:
            st.error(f"Error getting membership: {str(e)}")
            return {"plan": "basic", "features": self.membership_plans["basic"]["features"]}

    def render_membership_ui(self):
        """Renderizar interfaz de membresías"""
        st.header("🌟 Planes de Membresía")

        # Mostrar planes en columnas
        cols = st.columns(len(self.membership_plans))
        for i, (plan_type, plan) in enumerate(self.membership_plans.items()):
            with cols[i]:
                st.markdown(f"""
                <div style='
                    padding: 1.5rem;
                    background: {'linear-gradient(145deg, #1E2126 0%, #0E1117 100%)' if plan_type != 'basic' else 'none'};
                    border-radius: 10px;
                    border: 1px solid rgba(255,215,0,0.1);
                    height: 100%;
                '>
                    <h3 style='text-align: center;'>{plan['name']}</h3>
                    <div style='text-align: center; margin: 1rem 0;'>
                        <span style='font-size: 2rem;'>
                            {'Gratis' if plan['price'] == 0 else f'${plan["price"]}'}/mes
                        </span>
                    </div>
                    <ul style='list-style-type: none; padding: 0;'>
                        {"".join([f"<li style='margin: 0.5rem 0;'>✓ {feature}</li>" for feature in plan['features']])}
                    </ul>
                    <div style='text-align: center; margin-top: 1rem;'>
                        <button style='
                            background-color: #FFD700;
                            color: black;
                            padding: 0.5rem 1rem;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                        '>
                            {'Comenzar' if plan_type == 'basic' else 'Subscribirse'}
                        </button>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    def render_premium_ads(self, user_data: Dict):
        """Renderizar anuncios premium basados en el perfil del usuario"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, category, target_audience
                    FROM premium_ads
                    WHERE active = true
                    ORDER BY conversion_rate DESC
                    LIMIT 3
                """)
                ads = cur.fetchall()

                if ads:
                    st.markdown("### 🎯 Ofertas Especiales")
                    for ad in ads:
                        with st.container():
                            st.markdown(f"""
                            <div style='
                                padding: 1rem;
                                background: rgba(255,215,0,0.05);
                                border-radius: 10px;
                                margin: 0.5rem 0;
                                border: 1px solid rgba(255,215,0,0.1);
                            '>
                                <h4>{ad[1]}</h4>
                                <p>{ad[2]}</p>
                                <div style='text-align: right;'>
                                    <small>Categoría: {ad[3]}</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            if st.button("Más información", key=f"ad_{ad[0]}"):
                                self.track_conversion(
                                    user_data['id'],
                                    "ad_click",
                                    0,
                                    "premium_ad",
                                    {"ad_id": ad[0]}
                                )
        except Exception as e:
            st.error(f"Error rendering ads: {str(e)}")

    def get_conversion_metrics(self) -> Dict:
        """Obtener métricas de conversión"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_conversions,
                        SUM(value) as total_value,
                        AVG(value) as avg_value,
                        event_type,
                        source
                    FROM conversions
                    WHERE timestamp >= NOW() - INTERVAL '30 days'
                    GROUP BY event_type, source
                """)
                results = cur.fetchall()

                metrics = {
                    "total_conversions": 0,
                    "total_value": 0,
                    "avg_value": 0,
                    "by_source": {},
                    "by_event": {}
                }

                for row in results:
                    metrics["total_conversions"] += row[0]
                    metrics["total_value"] += row[1] or 0
                    metrics["by_source"][row[4]] = {
                        "conversions": row[0],
                        "value": row[1] or 0
                    }
                    metrics["by_event"][row[3]] = {
                        "conversions": row[0],
                        "value": row[1] or 0
                    }

                if metrics["total_conversions"] > 0:
                    metrics["avg_value"] = metrics["total_value"] / metrics["total_conversions"]

                return metrics
        except Exception as e:
            st.error(f"Error getting metrics: {str(e)}")
            return {}

    def render_admin_metrics(self):
        """Renderizar métricas para administradores"""
        st.header("📊 Métricas de Monetización")

        metrics = self.get_conversion_metrics()
        if not metrics:
            st.warning("No hay datos de conversión disponibles")
            return

        # Métricas principales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Conversiones Totales",
                metrics["total_conversions"]
            )
        with col2:
            st.metric(
                "Valor Total",
                f"${metrics['total_value']:,.2f}"
            )
        with col3:
            st.metric(
                "Valor Promedio",
                f"${metrics['avg_value']:,.2f}"
            )

        # Análisis por fuente
        st.subheader("Conversiones por Fuente")
        if metrics["by_source"]:
            source_data = pd.DataFrame({
                'Conversiones': {k: v['conversions'] for k, v in metrics["by_source"].items()}
            })
            st.bar_chart(source_data)
        else:
            st.info("No hay datos de conversión por fuente disponibles")

        # Análisis por tipo de evento
        st.subheader("Conversiones por Tipo de Evento")
        if metrics["by_event"]:
            event_data = pd.DataFrame({
                'Valor': {k: v['value'] for k, v in metrics["by_event"].items()}
            })
            st.bar_chart(event_data)
        else:
            st.info("No hay datos de conversión por tipo de evento disponibles")