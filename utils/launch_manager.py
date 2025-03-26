import streamlit as st
import psycopg2
import os
from datetime import datetime
from typing import Dict, List, Optional

class LaunchManager:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.setup_database()
        self.phases = {
            'beta': {
                'name': 'Beta',
                'description': 'Fase inicial con usuarios seleccionados',
                'max_users': 50,
                'features': ['análisis básico', 'portafolio demo']
            },
            'optimization': {
                'name': 'Optimización',
                'description': 'Mejoras basadas en feedback de usuarios',
                'max_users': 200,
                'features': ['análisis avanzado', 'portafolios múltiples']
            },
            'scaling': {
                'name': 'Escalamiento',
                'description': 'Apertura general y marketing',
                'max_users': None,
                'features': ['todas las características']
            }
        }

    def setup_database(self):
        """Configurar tablas necesarias"""
        try:
            with self.conn.cursor() as cur:
                # Tabla para control de fases
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS launch_phases (
                        id SERIAL PRIMARY KEY,
                        phase_name VARCHAR(50) NOT NULL,
                        is_active BOOLEAN DEFAULT false,
                        start_date TIMESTAMP,
                        end_date TIMESTAMP,
                        max_users INTEGER,
                        current_users INTEGER DEFAULT 0
                    )
                """)

                # Tabla para lista de espera
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS waitlist (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'pending',
                        invitation_sent BOOLEAN DEFAULT false,
                        invitation_date TIMESTAMP
                    )
                """)

                # Tabla para métricas de fase
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS phase_metrics (
                        id SERIAL PRIMARY KEY,
                        phase_name VARCHAR(50) NOT NULL,
                        metric_name VARCHAR(50) NOT NULL,
                        metric_value FLOAT,
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                self.conn.commit()
        except Exception as e:
            st.error(f"Error en setup: {str(e)}")

    def check_access_allowed(self, user_id: int) -> bool:
        """Verificar si un usuario tiene acceso permitido"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT w.status, lp.is_active, lp.max_users, lp.current_users
                    FROM waitlist w
                    JOIN launch_phases lp ON lp.is_active = true
                    WHERE w.id = %s
                """, (user_id,))
                result = cur.fetchone()

                if not result:
                    return False

                status, is_active, max_users, current_users = result
                return (status == 'approved' and is_active and 
                        (max_users is None or current_users < max_users))
        except Exception as e:
            st.error(f"Error verificando acceso: {str(e)}")
            return False

    def render_admin_launch_control(self):
        """Renderizar panel de control de lanzamiento para admin"""
        st.header("🚀 Control de Lanzamiento")

        # Selección de fase actual
        current_phase = st.selectbox(
            "Fase Actual",
            list(self.phases.keys()),
            format_func=lambda x: self.phases[x]['name']
        )

        # Mostrar detalles de la fase
        phase = self.phases[current_phase]
        features_list = "\n".join([f"- {feature}" for feature in phase['features']])

        st.markdown(f"""
        ### Fase: {phase['name']}
        {phase['description']}

        **Características activas:**
        {features_list}

        **Límite de usuarios:** {phase['max_users'] or 'Sin límite'}
        """)

        # Métricas de la fase actual
        col1, col2, col3 = st.columns(3)
        try:
            with self.conn.cursor() as cur:
                # Usuarios activos
                cur.execute("SELECT COUNT(*) FROM users WHERE last_login > NOW() - INTERVAL '7 days'")
                active_users = cur.fetchone()[0]
                col1.metric("Usuarios Activos", active_users)

                # Lista de espera
                cur.execute("SELECT COUNT(*) FROM waitlist WHERE status = 'pending'")
                waitlist_count = cur.fetchone()[0]
                col2.metric("En Lista de Espera", waitlist_count)

                # Conversión
                cur.execute("SELECT COUNT(*) FROM waitlist WHERE status = 'approved'")
                approved = cur.fetchone()[0]
                conversion = (approved / waitlist_count * 100) if waitlist_count > 0 else 0
                col3.metric("Tasa de Conversión", f"{conversion:.1f}%")
        except Exception as e:
            st.error(f"Error obteniendo métricas: {str(e)}")

        # Control de acceso
        st.subheader("Control de Acceso")
        with st.expander("Gestionar Lista de Espera"):
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        SELECT email, registration_date, status
                        FROM waitlist
                        WHERE status = 'pending'
                        ORDER BY registration_date ASC
                        LIMIT 50
                    """)
                    pending = cur.fetchall()

                    if pending:
                        for email, date, status in pending:
                            col1, col2, col3 = st.columns([3,2,1])
                            col1.text(email)
                            col2.text(date.strftime("%Y-%m-%d"))
                            if col3.button("Aprobar", key=f"approve_{email}"):
                                cur.execute("""
                                    UPDATE waitlist
                                    SET status = 'approved', invitation_sent = true,
                                        invitation_date = CURRENT_TIMESTAMP
                                    WHERE email = %s
                                """, (email,))
                                self.conn.commit()
                                st.success(f"Usuario {email} aprobado")
                                st.rerun()
                    else:
                        st.info("No hay usuarios pendientes en la lista de espera")
            except Exception as e:
                st.error(f"Error gestionando lista de espera: {str(e)}")

    def add_to_waitlist(self, email: str, name: str = None, notes: str = None) -> bool:
        """Añadir usuario a la lista de espera con información adicional"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO waitlist (email, name, notes, registration_date)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                """, (email, name, notes))
                self.conn.commit()
                
                # Notificar al admin por email (implementar después)
                return cur.fetchone() is not None
        except Exception as e:
            st.error(f"Error añadiendo a lista de espera: {str(e)}")
            return False

    def render_waitlist_ui(self):
        """Renderizar interfaz de lista de espera para usuarios"""
        st.markdown("""
        ## 🚀 ¡Próximamente!

        BROKER.IA está en fase de lanzamiento controlado.
        Únete a nuestra lista de espera para ser de los primeros en acceder.
        """)

        with st.form("waitlist_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email*", key="waitlist_email")
            with col2:
                name = st.text_input("Nombre", key="waitlist_name")
            
            notes = st.text_area("¿Por qué te interesa BROKER.IA?", height=100)
            
            if st.form_submit_button("Unirme a la Lista de Espera"):
                if not email:
                    st.error("Por favor, introduce tu email")
                elif self.add_to_waitlist(email, name, notes):
                    st.success("""
                        ¡Te has unido a la lista de espera! 
                        Te notificaremos cuando tu acceso esté listo.
                        """)
                    st.balloons()
                else:
                    st.error("Este email ya está en la lista de espera")