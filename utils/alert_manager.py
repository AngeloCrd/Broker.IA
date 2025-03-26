import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional

class Alert:
    def __init__(self, symbol: str, alert_type: str, condition: str, 
                 target_value: float, user_email: Optional[str] = None):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.symbol = symbol.upper()
        self.alert_type = alert_type  # 'price', 'volume', 'technical'
        self.condition = condition    # 'above', 'below'
        self.target_value = target_value
        self.user_email = user_email
        self.created_at = datetime.now()
        self.triggered = False
        self.last_check = None

class AlertManager:
    def __init__(self):
        if 'alerts' not in st.session_state:
            st.session_state.alerts = {}

    def add_alert(self, symbol: str, alert_type: str, condition: str, 
                  target_value: float, user_email: Optional[str] = None) -> str:
        """Añadir una nueva alerta"""
        alert = Alert(symbol, alert_type, condition, target_value, user_email)
        st.session_state.alerts[alert.id] = alert
        return alert.id

    def remove_alert(self, alert_id: str) -> bool:
        """Eliminar una alerta existente"""
        if alert_id in st.session_state.alerts:
            del st.session_state.alerts[alert_id]
            return True
        return False

    def get_alerts(self, symbol: Optional[str] = None) -> List[Alert]:
        """Obtener todas las alertas o filtrar por símbolo"""
        alerts = st.session_state.alerts.values()
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol.upper()]
        return list(alerts)

    def check_alerts(self, market_data: Dict[str, float]) -> List[Alert]:
        """Verificar si alguna alerta debe activarse"""
        triggered_alerts = []
        
        for alert in st.session_state.alerts.values():
            if alert.triggered:
                continue
                
            current_value = market_data.get(alert.symbol)
            if current_value is None:
                continue

            alert.last_check = datetime.now()
            
            if alert.condition == 'above' and current_value > alert.target_value:
                alert.triggered = True
                triggered_alerts.append(alert)
            elif alert.condition == 'below' and current_value < alert.target_value:
                alert.triggered = True
                triggered_alerts.append(alert)

        return triggered_alerts

    def format_alert_message(self, alert: Alert) -> str:
        """Formatear mensaje de alerta para notificación"""
        condition_text = "superado" if alert.condition == "above" else "caído por debajo de"
        return f"""
        🔔 Alerta de {alert.symbol}
        
        El {alert.alert_type} ha {condition_text} {alert.target_value}
        
        Configurado el: {alert.created_at.strftime("%Y-%m-%d %H:%M")}
        Activado el: {datetime.now().strftime("%Y-%m-%d %H:%M")}
        """
