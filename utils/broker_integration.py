import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List

class BrokerConnection:
    def __init__(self, broker_name: str, user_id: str = None):
        self.broker_name = broker_name
        self.user_id = user_id
        self.last_sync = None
        self.positions = []

    def connect_with_file(self, portfolio_file) -> bool:
        """Conectar usando archivo de cartera"""
        try:
            if portfolio_file:
                # Procesar archivo CSV/Excel con datos de cartera
                df = pd.read_csv(portfolio_file) if portfolio_file.name.endswith('.csv') \
                    else pd.read_excel(portfolio_file)

                # Mapear columnas comunes
                mapping = {
                    'Instrument': 'symbol',
                    'Units': 'shares',
                    'Amount': 'shares',
                    'Quantity': 'shares',
                }
                df = df.rename(columns=mapping)

                # Asegurar columnas necesarias
                required_columns = ['symbol', 'shares']
                if not all(col in df.columns for col in required_columns):
                    st.error("El archivo debe contener las columnas 'symbol' y 'shares'")
                    return False

                # Seleccionar solo las columnas necesarias
                df = df[['symbol', 'shares']]

                # Guardar datos
                self.positions = df.to_dict('records')
                self.last_sync = datetime.now()
                return True
            return False
        except Exception as e:
            st.error(f"Error procesando archivo: {str(e)}")
            return False

    def get_positions(self) -> List[Dict]:
        """Obtener posiciones actuales"""
        return self.positions

class PortfolioAggregator:
    def __init__(self):
        self.brokers: Dict[str, BrokerConnection] = {}

    def render_manual_import_guide(self):
        """Mostrar guía de importación manual"""
        st.markdown("""
        ### 📝 Importar Cartera Manualmente

        Para importar tu cartera:

        1. **Prepara tu archivo Excel/CSV con:**
           - Columna 'symbol': Símbolo de la acción (ej: AAPL)
           - Columna 'shares': Número de acciones

        2. **Guarda el archivo** en formato Excel (.xlsx) o CSV (.csv)
        """)

        # Sección para importar cartera
        portfolio_name = st.text_input("Nombre de la Cartera")
        portfolio_file = st.file_uploader("Subir archivo (CSV/Excel)", type=['csv', 'xlsx'])

        if st.button("Importar Cartera"):
            if portfolio_name and portfolio_file:
                broker = BrokerConnection(portfolio_name)
                if broker.connect_with_file(portfolio_file):
                    self.brokers[portfolio_name] = broker
                    st.success(f"Cartera '{portfolio_name}' importada correctamente")
                    st.rerun()

    def render_connected_portfolios(self):
        """Mostrar todas las carteras"""
        st.subheader("📊 Gestión de Carteras")
        
        # Obtener carteras del usuario actual
        user = st.session_state.auth_manager.get_current_user()
        portfolios = st.session_state.portfolios
        
        if not portfolios:
            st.info("No hay carteras aún. Crea tu primera cartera en la sección 'Gestión Manual'.")
            return

        for name, portfolio in portfolios.items():
            with st.expander(f"📊 {name}", expanded=True):
                positions = portfolio.get_positions()
                if not positions.empty:
                    st.markdown("**Posiciones actuales:**")
                    st.dataframe(
                        positions.style.format({
                            'Shares': '{:.2f}',
                            'Current Price': '${:.2f}',
                            'Market Value': '${:.2f}',
                            'Gain/Loss': '${:.2f}',
                            'Return %': '{:.2f}%'
                        }),
                        use_container_width=True
                    )
                    
                    # Añadir nueva posición
                    col1, col2 = st.columns(2)
                    with col1:
                        new_symbol = st.text_input("Símbolo", key=f"symbol_{name}")
                    with col2:
                        new_shares = st.number_input("Acciones", min_value=0.0, step=0.01, key=f"shares_{name}")
                        
                    if st.button("➕ Añadir Posición", key=f"add_{name}"):
                        try:
                            portfolio.add_position(new_symbol.upper(), new_shares)
                            portfolio.save()
                            st.success(f"Posición añadida: {new_symbol.upper()}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.warning("No hay posiciones en esta cartera")
                    
                # Eliminar cartera
                if st.button("🗑️ Eliminar Cartera", key=f"delete_{name}"):
                    try:
                        # Eliminar de la base de datos
                        with portfolio.conn.cursor() as cur:
                            cur.execute("DELETE FROM positions WHERE portfolio_id IN (SELECT id FROM portfolios WHERE name = %s AND user_id = %s)", 
                                      (name, user['id']))
                            cur.execute("DELETE FROM portfolios WHERE name = %s AND user_id = %s", 
                                      (name, user['id']))
                            portfolio.conn.commit()
                        
                        # Eliminar de la sesión
                        del st.session_state.portfolios[name]
                        st.success("Cartera eliminada")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar cartera: {str(e)}")

# Example usage
if __name__ == "__main__":
    portfolio = PortfolioAggregator()
    portfolio.render_manual_import_guide()
    portfolio.render_connected_portfolios()