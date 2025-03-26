import streamlit as st
from streamlit.components.v1 import components
import bcrypt
import jwt
import psycopg2
from datetime import datetime, timedelta
import os
from typing import Optional, Dict
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AuthManager:
    def __init__(self):
        self.conn = None
        self.connect_to_db()
        if 'user' not in st.session_state:
            st.session_state.user = None

    def connect_to_db(self):
        """Establecer conexión a la base de datos con reintentos"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                db_url = os.environ.get('DATABASE_URL')
                if not db_url:
                    st.error("Error: DATABASE_URL no está configurada")
                    return False

                # Asegurar que la URL tiene los parámetros correctos
                if '?' not in db_url:
                    db_url += '?sslmode=require'

                self.conn = psycopg2.connect(
                    db_url,
                    connect_timeout=10
                )
                self.setup_database()
                return True
            except psycopg2.Error as e:
                retry_count += 1
                if retry_count == max_retries:
                    st.error(f"Error de conexión a la base de datos: {str(e)}")
                    raise Exception("No se pudo establecer conexión con la base de datos")
                st.warning(f"Reintentando conexión ({retry_count}/{max_retries})...")

    def ensure_connection(self):
        """Asegurar que la conexión está activa"""
        try:
            # Intentar una consulta simple para verificar la conexión
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (psycopg2.Error, AttributeError):
            # Reconectar si hay error
            self.connect_to_db()

    def setup_database(self):
        """Configurar tablas necesarias en la base de datos"""
        try:
            with self.conn.cursor() as cur:
                # Crear tabla de usuarios si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        role VARCHAR(50) DEFAULT 'user',
                        email_verified BOOLEAN DEFAULT FALSE,
                        verification_token VARCHAR(255),
                        remember_token VARCHAR(255),
                        token_expires_at TIMESTAMP
                    )
                """)
                self.conn.commit()
        except Exception as e:
            st.error(f"Error configurando la base de datos: {str(e)}")

    def send_verification_email(self, email: str, token: str):
        """Enviar correo de verificación"""
        try:
            subject = "Verifica tu cuenta en BROKER.IA"
            body = f"""
            ¡Bienvenido a BROKER.IA!

            Para verificar tu cuenta, haz clic en el siguiente enlace:
            http://localhost:5000/verify?token={token}

            Si no creaste una cuenta, puedes ignorar este mensaje.

            Saludos,
            El equipo de BROKER.IA
            """

            msg = MIMEMultipart()
            msg['From'] = "noreply@broker-ia.com"
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Para demostración, guardar el token en la sesión
            st.session_state.verification_token = token
            return True
        except Exception as e:
            st.error(f"Error enviando email: {str(e)}")
            return False

    def generate_token(self, user_id: int, token_type: str = "verification") -> str:
        """Generar token único"""
        try:
            self.ensure_connection()
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=1)

            with self.conn.cursor() as cur:
                if token_type == "verification":
                    cur.execute(
                        "UPDATE users SET verification_token = %s WHERE id = %s",
                        (token, user_id)
                    )
                else:  # remember token
                    cur.execute(
                        "UPDATE users SET remember_token = %s, token_expires_at = %s WHERE id = %s",
                        (token, expires_at, user_id)
                    )
                self.conn.commit()
            return token
        except Exception as e:
            st.error(f"Error generando token: {str(e)}")
            return None

    def verify_email(self, token: str) -> bool:
        """Verificar email con token"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users 
                    SET email_verified = TRUE, verification_token = NULL
                    WHERE verification_token = %s
                    RETURNING id
                    """,
                    (token,)
                )
                result = cur.fetchone()
                self.conn.commit()
                return result is not None
        except Exception as e:
            st.error(f"Error verificando email: {str(e)}")
            return False

    def create_remember_token(self, user_id: int) -> str:
        """Crear token para recordar sesión"""
        return self.generate_token(user_id, "remember")

    def check_remember_token(self, token: str) -> Optional[Dict]:
        """Verificar token de recordar sesión"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, name, role 
                    FROM users 
                    WHERE remember_token = %s AND token_expires_at > NOW()
                    """,
                    (token,)
                )
                user = cur.fetchone()
                if user:
                    return {
                        'id': user[0],
                        'email': user[1],
                        'name': user[2],
                        'role': user[3]
                    }
                return None
        except Exception as e:
            st.error(f"Error verificando token: {str(e)}")
            return None

    def hash_password(self, password: str) -> str:
        """Hash la contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar si la contraseña coincide con el hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def register_user(self, email: str, password: str, name: str) -> bool:
        """Registrar un nuevo usuario"""
        try:
            self.ensure_connection()

            # Verificar si el email ya existe
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    st.error("Este email ya está registrado")
                    return False

            password_hash = self.hash_password(password)
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password_hash, name, email_verified)
                    VALUES (%s, %s, %s, false)
                    RETURNING id
                    """,
                    (email, password_hash, name)
                )
                result = cur.fetchone()
                if not result:
                    st.error("Error al crear el usuario")
                    return False

                user_id = result[0]
                self.conn.commit()

                # Generar y enviar token de verificación
                token = self.generate_token(user_id)
                if token:
                    self.send_verification_email(email, token)
                    return True
                return False
        except psycopg2.Error as e:
            self.conn = None  # Forzar reconexión en el próximo intento
            st.error(f"Error en la base de datos: {str(e)}")
            return False
        except Exception as e:
            st.error(f"Error inesperado: {str(e)}")
            return False

    def login_user(self, email: str, password: str, remember: bool = False) -> bool:
        """Iniciar sesión de usuario"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT id, password_hash, name, role, email_verified FROM users WHERE email = %s",
                    (email,)
                )
                user = cur.fetchone()

                if not user:
                    st.error("Usuario no encontrado")
                    return False

                if not self.verify_password(password, user[1]):
                    st.error("Contraseña incorrecta")
                    return False

                # Temporalmente deshabilitamos la verificación de email para pruebas
                #if not user[4]:  # email no verificado
                #    st.warning("Por favor, verifica tu correo electrónico antes de iniciar sesión.")
                #    return False

                # Actualizar último login
                cur.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                    (user[0],)
                )
                self.conn.commit()

                # Guardar información del usuario en la sesión
                st.session_state.user = {
                    'id': user[0],
                    'email': email,
                    'name': user[2],
                    'role': user[3]
                }

                # Cargar carteras del usuario
                from utils.portfolio import Portfolio
                st.session_state.portfolios = Portfolio.load_user_portfolios(user[0])

                # Crear token de recordar si se solicitó
                if remember:
                    remember_token = self.create_remember_token(user[0])
                    st.session_state.remember_token = remember_token

                return True
        except psycopg2.Error as e:
            st.error(f"Error al iniciar sesión: {str(e)}")
            return False

    def logout_user(self):
        """Cerrar sesión de usuario"""
        if 'remember_token' in st.session_state:
            try:
                self.ensure_connection()
                with self.conn.cursor() as cur:
                    cur.execute(
                        "UPDATE users SET remember_token = NULL, token_expires_at = NULL WHERE id = %s",
                        (st.session_state.user['id'],)
                    )
                    self.conn.commit()
                del st.session_state.remember_token
            except Exception as e:
                st.error(f"Error al cerrar sesión: {str(e)}")
        st.session_state.user = None

    def get_current_user(self) -> Optional[Dict]:
        """Obtener usuario actual"""
        if not st.session_state.get('user'):
            # Intentar recuperar token desde una cookie oculta
            import streamlit.components.v1 as components
            
            cookie_retrieve = components.html(
                """
                <div id="tokenContainer"></div>
                <script>
                    function getCookie(name) {
                        const value = `; ${document.cookie}`;
                        const parts = value.split(`; ${name}=`);
                        if (parts.length === 2) {
                            const token = parts.pop().split(';').shift();
                            document.getElementById('tokenContainer').innerText = token;
                            return token;
                        }
                        return '';
                    }
                    getCookie('remember_token');
                </script>
                """,
                height=0
            )

            # Intentar usar el token para recuperar la sesión
            remember_token = st.session_state.get('remember_token')
            if remember_token:
                user = self.check_remember_token(remember_token)
                if user:
                    st.session_state.user = user
                    # Actualizar cookie
                    components.html(
                        f"""
                        <script>
                            const d = new Date();
                            d.setTime(d.getTime() + (30*24*60*60*1000));
                            document.cookie = "remember_token={remember_token};path=/;expires=" + d.toUTCString() + ";SameSite=Lax";
                        </script>
                        """,
                        height=0
                    )
                    return user

        return st.session_state.get('user')

    def is_authenticated(self) -> bool:
        """Verificar si hay un usuario autenticado"""
        return self.get_current_user() is not None

    def is_admin(self) -> bool:
        """Verificar si el usuario actual es administrador"""
        user = self.get_current_user()
        return user is not None and user.get('email') == 'angelortegoz@gmail.com'

    def render_login_ui(self):
        """Renderizar interfaz de login/registro"""
        if not self.is_authenticated():
            tabs = st.tabs(["Iniciar Sesión", "Registrarse"])

            with tabs[0]:
                with st.form("login_form", clear_on_submit=True):
                    st.markdown("""
                        <h3 style='text-align: center; margin-bottom: 1rem;'>
                            👋 ¡Bienvenido de nuevo!
                        </h3>
                    """, unsafe_allow_html=True)

                    email = st.text_input("Email", key="login_email")
                    password = st.text_input("Contraseña", type="password", key="login_password")
                    remember = st.checkbox("Recordar sesión", key="remember_me")

                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                            if self.login_user(email, password, remember):
                                st.success("¡Sesión iniciada correctamente!")
                                st.rerun()

            with tabs[1]:
                with st.form("register_form", clear_on_submit=True):
                    st.markdown("""
                        <h3 style='text-align: center; margin-bottom: 1rem;'>
                            🚀 Únete a BROKER.IA
                        </h3>
                    """, unsafe_allow_html=True)

                    name = st.text_input("Nombre", key="reg_name")
                    email = st.text_input("Email", key="reg_email")
                    password = st.text_input("Contraseña", type="password", key="reg_password")
                    password_confirm = st.text_input("Confirmar Contraseña", type="password", key="reg_password_confirm")

                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        if st.form_submit_button("Registrarse", use_container_width=True):
                            if not all([name, email, password, password_confirm]):
                                st.error("Por favor, completa todos los campos")
                            elif password != password_confirm:
                                st.error("Las contraseñas no coinciden")
                            elif self.register_user(email, password, name):
                                st.success("""
                                    ¡Registro exitoso! 
                                    Te hemos enviado un correo de verificación.
                                    Por favor, verifica tu email antes de iniciar sesión.
                                """)
                                # Para demostración, mostrar el token
                                if 'verification_token' in st.session_state:
                                    st.info(f"""
                                        Token de verificación (demo): 
                                        {st.session_state.verification_token}
                                    """)
        else:
            user = self.get_current_user()
            st.sidebar.markdown(f"👋 Bienvenido, {user['name']}!")
            if st.sidebar.button("Cerrar Sesión"):
                self.logout_user()
                st.rerun()

def require_auth(func):
    """Decorador para requerir autenticación en una página"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('user'):
            st.warning("Por favor, inicia sesión para acceder a esta página")
            return False
        return func(*args, **kwargs)
    return wrapper