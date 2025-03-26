import streamlit as st

def render_loading_screen(message: str = "Cargando..."):
    """Renderizar pantalla de carga animada con mascota financiera"""
    st.markdown("""
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-10deg); }
        75% { transform: rotate(10deg); }
    }
    
    .mascot-container {
        text-align: center;
        padding: 2rem;
        animation: bounce 2s infinite ease-in-out;
    }
    
    .mascot {
        font-size: 5rem;
        display: inline-block;
        animation: wave 2s infinite ease-in-out;
    }
    
    .loading-text {
        font-size: 1.5rem;
        margin-top: 1rem;
        color: #FFD700;
    }
    
    .loading-dots::after {
        content: '...';
        animation: dots 1.5s steps(4, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60% { content: '...'; }
        80%, 100% { content: ''; }
    }
    </style>
    
    <div class="mascot-container">
        <div class="mascot">🦊</div>
        <div class="loading-text">
            {message}<span class="loading-dots"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_loading_overlay():
    """Mostrar overlay de carga sobre toda la pantalla"""
    st.markdown("""
    <style>
    #loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(14, 17, 23, 0.9);
        z-index: 999999;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: opacity 0.3s ease-out;
        opacity: 1;
    }
    #loading-overlay.hidden {
        opacity: 0;
        pointer-events: none;
    }
    </style>
    
    <div id="loading-overlay">
        <div class="mascot-container">
            <div class="mascot">🦊</div>
            <div class="loading-text">
                Preparando tu experiencia<span class="loading-dots"></span>
            </div>
        </div>
    </div>
    <script>
        setTimeout(() => {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) overlay.classList.add('hidden');
        }, 3000);
    </script>
    """, unsafe_allow_html=True)

def remove_loading_overlay():
    """Remover overlay de carga"""
    st.markdown("""
    <style>
    #loading-overlay {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    .mascot-container {
        display: none !important;
    }
    </style>
    <script>
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.remove();
    </script>
    """, unsafe_allow_html=True)
