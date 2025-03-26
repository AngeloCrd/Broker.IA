from typing import Dict, List, Optional
import streamlit as st

class BrokerFeature:
    def __init__(self, name: str, description: str, supported: bool = False):
        self.name = name
        self.description = description
        self.supported = supported

class BrokerCompatibility:
    def __init__(self):
        # Definir características comunes de los brokers
        self.common_features = {
            "real_time_data": BrokerFeature(
                "Datos en Tiempo Real",
                "Cotizaciones y datos de mercado en tiempo real"
            ),
            "historical_data": BrokerFeature(
                "Datos Históricos",
                "Acceso a datos históricos de precios y volumen"
            ),
            "portfolio_sync": BrokerFeature(
                "Sincronización de Cartera",
                "Sincronización automática de posiciones y operaciones"
            ),
            "order_execution": BrokerFeature(
                "Ejecución de Órdenes",
                "Capacidad para ejecutar órdenes de trading"
            ),
            "multi_account": BrokerFeature(
                "Múltiples Cuentas",
                "Soporte para gestionar múltiples cuentas"
            )
        }

        # Definir compatibilidad por broker
        self.broker_compatibility = {
            "Interactive Brokers": {
                "api_version": "Client Portal API 3.0",
                "connection_type": "REST API",
                "documentation": "https://interactivebrokers.github.io/cpwebapi/",
                "features": {
                    "real_time_data": True,
                    "historical_data": True,
                    "portfolio_sync": True,
                    "order_execution": True,
                    "multi_account": True
                },
                "requirements": [
                    "Cuenta de Interactive Brokers activa",
                    "Credenciales de acceso al Client Portal",
                    "2FA habilitado (recomendado)"
                ]
            },
            "Degiro": {
                "api_version": "API v1.0",
                "connection_type": "REST API",
                "documentation": "https://developer.degiro.com/",
                "features": {
                    "real_time_data": True,
                    "historical_data": True,
                    "portfolio_sync": True,
                    "order_execution": False,
                    "multi_account": False
                },
                "requirements": [
                    "Cuenta Degiro activa",
                    "Usuario y contraseña",
                    "Aceptación de términos de API"
                ]
            },
            "eToro": {
                "api_version": "eToroAPI v2",
                "connection_type": "REST API",
                "documentation": "https://api.etoro.com/docs",
                "features": {
                    "real_time_data": True,
                    "historical_data": True,
                    "portfolio_sync": True,
                    "order_execution": False,
                    "multi_account": False
                },
                "requirements": [
                    "Cuenta eToro verificada",
                    "API Key personal",
                    "Modo de solo lectura habilitado"
                ]
            },
            "Trading 212": {
                "api_version": "T212 API Beta",
                "connection_type": "REST API",
                "documentation": "https://t212.com/api",
                "features": {
                    "real_time_data": True,
                    "historical_data": True,
                    "portfolio_sync": True,
                    "order_execution": False,
                    "multi_account": False
                },
                "requirements": [
                    "Cuenta Trading 212 activa",
                    "Autenticación de dos factores",
                    "Aceptación de términos de API"
                ]
            },
            "XM": {
                "api_version": "XM Trading API v1",
                "connection_type": "REST API",
                "documentation": "https://xm.com/api-documentation",
                "features": {
                    "real_time_data": True,
                    "historical_data": True,
                    "portfolio_sync": True,
                    "order_execution": False,
                    "multi_account": True
                },
                "requirements": [
                    "Cuenta XM verificada",
                    "API Key generada",
                    "IP registrada"
                ]
            }
        }

    def check_compatibility(self, broker_name: str) -> Dict:
        """Verificar compatibilidad de un broker específico"""
        if broker_name not in self.broker_compatibility:
            return None
        
        broker_info = self.broker_compatibility[broker_name]
        features = {}
        
        for feature_key, feature_obj in self.common_features.items():
            feature = BrokerFeature(
                feature_obj.name,
                feature_obj.description,
                broker_info["features"].get(feature_key, False)
            )
            features[feature_key] = feature
            
        return {
            "api_version": broker_info["api_version"],
            "connection_type": broker_info["connection_type"],
            "documentation": broker_info["documentation"],
            "features": features,
            "requirements": broker_info["requirements"]
        }

    def render_compatibility_ui(self):
        """Renderizar interfaz de verificación de compatibilidad"""
        st.subheader("Verificador de Compatibilidad")
        
        selected_broker = st.selectbox(
            "Seleccionar Broker",
            list(self.broker_compatibility.keys())
        )

        if selected_broker:
            compatibility = self.check_compatibility(selected_broker)
            
            if compatibility:
                # Información técnica
                st.markdown("""
                    <div style='
                        background: rgba(49,51,63,0.1);
                        border-radius: 10px;
                        padding: 1rem;
                        margin: 1rem 0;
                    '>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Versión API:** {compatibility['api_version']}")
                with col2:
                    st.markdown(f"**Tipo de Conexión:** {compatibility['connection_type']}")
                
                st.markdown("</div>", unsafe_allow_html=True)

                # Características soportadas
                st.subheader("Características Soportadas")
                features_cols = st.columns(2)
                
                for idx, (_, feature) in enumerate(compatibility['features'].items()):
                    with features_cols[idx % 2]:
                        st.markdown(f"""
                            <div style='
                                padding: 1rem;
                                background: rgba(49,51,63,0.05);
                                border-radius: 8px;
                                margin-bottom: 0.5rem;
                            '>
                                <div style='display: flex; align-items: center; justify-content: space-between;'>
                                    <span>{feature.name}</span>
                                    <span style='
                                        color: {"#00FF00" if feature.supported else "#FF4444"};
                                        font-weight: bold;
                                    '>
                                        {"Soportado" if feature.supported else "No Soportado"}
                                    </span>
                                </div>
                                <p style='
                                    font-size: 0.9rem;
                                    opacity: 0.8;
                                    margin: 0.5rem 0 0 0;
                                '>{feature.description}</p>
                            </div>
                        """, unsafe_allow_html=True)

                # Requisitos
                st.subheader("Requisitos de Conexión")
                for req in compatibility['requirements']:
                    st.markdown(f"""
                        <div style='
                            padding: 0.5rem;
                            background: rgba(49,51,63,0.05);
                            border-radius: 8px;
                            margin-bottom: 0.5rem;
                        '>
                            • {req}
                        </div>
                    """, unsafe_allow_html=True)

                # Documentación
                st.markdown(f"""
                    <div style='margin-top: 2rem;'>
                        <a href='{compatibility["documentation"]}' 
                           target='_blank'
                           style='
                               display: inline-block;
                               padding: 0.5rem 1rem;
                               background: rgba(49,51,63,0.2);
                               border-radius: 5px;
                               text-decoration: none;
                               color: inherit;
                           '>
                            Ver Documentación API
                        </a>
                    </div>
                """, unsafe_allow_html=True)

# Example usage
if __name__ == "__main__":
    compatibility_checker = BrokerCompatibility()
    compatibility_checker.render_compatibility_ui()
