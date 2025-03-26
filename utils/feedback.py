
import streamlit as st
from datetime import datetime
from typing import Dict, List

class FeedbackManager:
    def __init__(self):
        if 'feedback_items' not in st.session_state:
            st.session_state.feedback_items = []
            
    def add_feedback(self, type: str, content: str, user_email: str):
        """Añadir nuevo feedback"""
        feedback = {
            'id': len(st.session_state.feedback_items) + 1,
            'type': type,
            'content': content,
            'user_email': user_email,
            'timestamp': datetime.now(),
            'votes': 0,
            'status': 'pending'
        }
        st.session_state.feedback_items.append(feedback)
        
    def get_all_feedback(self) -> List[Dict]:
        """Obtener todo el feedback ordenado por votos"""
        return sorted(
            st.session_state.feedback_items,
            key=lambda x: x['votes'],
            reverse=True
        )
        
    def vote_feedback(self, feedback_id: int):
        """Votar por un feedback"""
        for item in st.session_state.feedback_items:
            if item['id'] == feedback_id:
                item['votes'] += 1
                break
                
    def render_feedback_ui(self):
        """Renderizar interfaz de feedback"""
        st.header("💡 Feedback y Sugerencias")
        
        # Formulario para nuevo feedback
        with st.form("new_feedback"):
            feedback_type = st.selectbox(
                "Tipo de Feedback",
                ["Sugerencia", "Bug", "Mejora", "Otro"]
            )
            content = st.text_area("Tu Feedback", height=100)
            
            if st.form_submit_button("Enviar Feedback"):
                if content:
                    user = st.session_state.auth_manager.get_current_user()
                    self.add_feedback(feedback_type, content, user['email'])
                    st.success("¡Gracias por tu feedback!")
                else:
                    st.error("Por favor, escribe tu feedback")
        
        # Mostrar feedback existente
        st.subheader("Feedback de la Comunidad")
        
        for item in self.get_all_feedback():
            with st.container():
                col1, col2 = st.columns([4,1])
                
                with col1:
                    st.markdown(f"""
                    **{item['type']}** - {item['timestamp'].strftime('%Y-%m-%d %H:%M')}  
                    {item['content']}
                    """)
                    
                with col2:
                    st.button(
                        f"👍 {item['votes']}",
                        key=f"vote_{item['id']}",
                        on_click=lambda: self.vote_feedback(item['id'])
                    )
                
                st.markdown("---")
