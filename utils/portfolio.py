import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import psycopg2
import os
from datetime import datetime, timedelta

class Portfolio:
    def __init__(self, name, user_id=None):
        self.name = name
        self.user_id = user_id
        self.positions = pd.DataFrame(columns=['symbol', 'shares', 'cost_basis'])
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        
        # Crear tabla si no existe
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id SERIAL PRIMARY KEY,
                    portfolio_id INTEGER REFERENCES portfolios(id),
                    symbol VARCHAR(20),
                    shares FLOAT,
                    cost_basis FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            
    def save(self):
        """Guardar cartera y posiciones en la base de datos"""
        try:
            with self.conn.cursor() as cur:
                # Guardar o actualizar cartera
                cur.execute("""
                    INSERT INTO portfolios (user_id, name)
                    VALUES (%s, %s)
                    RETURNING id
                """, (self.user_id, self.name))
                portfolio_id = cur.fetchone()[0]
                
                # Eliminar posiciones anteriores
                cur.execute("DELETE FROM positions WHERE portfolio_id = %s", (portfolio_id,))
                
                # Guardar nuevas posiciones
                for _, position in self.positions.iterrows():
                    cur.execute("""
                        INSERT INTO positions (portfolio_id, symbol, shares, cost_basis)
                        VALUES (%s, %s, %s, %s)
                    """, (portfolio_id, position['symbol'], position['shares'], position['cost_basis']))
                
                self.conn.commit()
        except Exception as e:
            print(f"Error saving portfolio: {str(e)}")
            self.conn.rollback()
            
    @staticmethod
    def load_user_portfolios(user_id):
        """Cargar todas las carteras de un usuario"""
        try:
            conn = psycopg2.connect(os.environ['DATABASE_URL'])
            portfolios = {}
            
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM portfolios WHERE user_id = %s", (user_id,))
                for portfolio_id, name in cur.fetchall():
                    portfolio = Portfolio(name, user_id)
                    
                    # Cargar posiciones
                    cur.execute("""
                        SELECT symbol, shares, cost_basis 
                        FROM positions 
                        WHERE portfolio_id = %s
                    """, (portfolio_id,))
                    
                    positions_data = []
                    for symbol, shares, cost_basis in cur.fetchall():
                        positions_data.append({
                            'symbol': symbol,
                            'shares': shares,
                            'cost_basis': cost_basis
                        })
                    
                    if positions_data:
                        portfolio.positions = pd.DataFrame(positions_data)
                    
                    portfolios[name] = portfolio
                    
            return portfolios
        except Exception as e:
            print(f"Error loading portfolios: {str(e)}")
            return {}
        
    def add_position(self, symbol: str, shares: float):
        """Add a new position or update existing one"""
        try:
            # Verify the symbol exists
            stock = yf.Ticker(symbol)
            current_price = stock.info['regularMarketPrice']
            
            # Update existing position or add new one
            if symbol in self.positions['symbol'].values:
                self.positions.loc[self.positions['symbol'] == symbol, 'shares'] += shares
            else:
                new_position = pd.DataFrame({
                    'symbol': [symbol],
                    'shares': [shares],
                    'cost_basis': [current_price]
                })
                self.positions = pd.concat([self.positions, new_position], ignore_index=True)
                
        except Exception as e:
            raise Exception(f"Error adding position: {str(e)}")
    
    def get_positions(self) -> pd.DataFrame:
        """Get current positions with latest market values"""
        if self.positions.empty:
            return pd.DataFrame()
        
        result = []
        for _, position in self.positions.iterrows():
            try:
                stock = yf.Ticker(position['symbol'])
                current_price = stock.info['regularMarketPrice']
                market_value = current_price * position['shares']
                gain_loss = market_value - (position['cost_basis'] * position['shares'])
                
                result.append({
                    'Symbol': position['symbol'],
                    'Shares': position['shares'],
                    'Current Price': current_price,
                    'Market Value': market_value,
                    'Gain/Loss': gain_loss,
                    'Return %': (gain_loss / (position['cost_basis'] * position['shares'])) * 100
                })
            except Exception as e:
                print(f"Error getting position data for {position['symbol']}: {str(e)}")
                
        return pd.DataFrame(result)
    
    def get_total_value(self) -> float:
        """Calculate total portfolio value"""
        positions = self.get_positions()
        return positions['Market Value'].sum() if not positions.empty else 0.0
    
    def get_performance_history(self) -> pd.DataFrame:
        """Get historical performance data"""
        if self.positions.empty:
            return pd.DataFrame()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        portfolio_history = pd.DataFrame()
        for _, position in self.positions.iterrows():
            try:
                stock = yf.Ticker(position['symbol'])
                history = stock.history(start=start_date, end=end_date)
                if not history.empty:
                    portfolio_history[position['symbol']] = history['Close'] * position['shares']
            except Exception as e:
                print(f"Error getting history for {position['symbol']}: {str(e)}")
        
        portfolio_history['Total'] = portfolio_history.sum(axis=1)
        return portfolio_history
    
    def create_performance_chart(self, performance_data: pd.DataFrame) -> go.Figure:
        """Create an interactive performance chart"""
        if performance_data.empty:
            return go.Figure()
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=performance_data.index,
                y=performance_data['Total'],
                name=self.name,
                line=dict(color='blue')
            )
        )
        
        fig.update_layout(
            title=f"{self.name} Performance",
            xaxis_title="Date",
            yaxis_title="Value ($)",
            showlegend=True
        )
        
        return fig
