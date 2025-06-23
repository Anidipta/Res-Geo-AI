import streamlit as st
from styles import apply_custom_styles
from map import render_map_page

def main():
    st.set_page_config(
        page_title="Res Geo AI",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_custom_styles()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    render_home_page() if st.session_state.current_page == 'home' else render_map_page()

def render_home_page():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-content">
                <h1 class="hero-title">🗺️ Res Geo AI</h1>
                <p class="hero-subtitle">Advanced Geospatial Intelligence for Indian Political Mapping</p>
                <div class="features-grid">
                    <div class="feature-card">
                        <h3>🎯 State Analysis</h3>
                        <p>Interactive state-wise political mapping</p>
                    </div>
                    <div class="feature-card">
                        <h3>🔍 Tile Generation</h3>
                        <p>High-resolution map tiling system</p>
                    </div>
                    <div class="feature-card">
                        <h3>📊 Data Visualization</h3>
                        <p>Advanced geospatial data insights</p>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Go to Map", help="Access Interactive Map"):
            st.session_state.current_page = 'map'
            st.rerun()

if __name__ == "__main__":
    main()