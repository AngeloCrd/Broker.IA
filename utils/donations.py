
import streamlit as st
import streamlit.components.v1 as components
import stripe
from datetime import datetime
import os

class DonationManager:
    def __init__(self):
        self.stripe_public_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        if 'donations' not in st.session_state:
            st.session_state.donations = []
            
    def add_donation(self, amount: float, donor_name: str, message: str = ""):
        """Registrar una nueva donación"""
        donation = {
            'id': len(st.session_state.donations) + 1,
            'amount': amount,
            'donor_name': donor_name,
            'message': message,
            'timestamp': datetime.now(),
            'status': 'completed'
        }
        st.session_state.donations.append(donation)
        
    def create_checkout_session(self, amount):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': int(amount * 100),
                        'product_data': {
                            'name': 'Donación',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=st.get_option('server.baseUrlPath') + '?success=true',
                cancel_url=st.get_option('server.baseUrlPath') + '?canceled=true',
            )
            return checkout_session.url
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
        
    def render_donation_ui(self):
        """Renderizar interfaz de donaciones"""
        st.header("💝 Apoya el Proyecto")
        
        st.markdown("""
        ¡Gracias por considerar apoyar este proyecto! Tu donación nos ayuda a seguir mejorando y desarrollando nuevas funcionalidades.
        """)
        
        components.html("""
            <script async src="https://js.stripe.com/v3/buy-button.js"></script>
            <stripe-buy-button
                buy-button-id="buy_btn_1R6Wf7HD3etGCYZR4XXbHkM7"
                publishable-key="pk_live_51R6W6VHD3etGCYZR8vVEE5AV6OLS1h0tgobo70YlraYFuYeou2I6C4AUG59HGPSuTfDe6kgb904iXNThkYqP8BWJ0054yfsS6E"
            >
            </stripe-buy-button>
        """, height=100)
        
        # Mostrar últimas donaciones
        if st.session_state.donations:
            st.subheader("❤️ Últimas Donaciones")
            for donation in reversed(st.session_state.donations[-5:]):
                st.markdown(f"""
                **{donation['donor_name']}** - {donation['amount']:.2f}€  
                _{donation['message'] if donation['message'] else 'Sin mensaje'}_
                """)
