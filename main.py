import streamlit as st
import base64
from pathlib import Path
from styles import apply_custom_styles
from map import render_map_page
from components import flood

flood.initialize_flood_model()

def get_base64_logo():
    """Convert logo to base64 string"""
    try:
        logo_path = Path("src/images/LOGO_ResGeoAI.png")
        if logo_path.exists():
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        else:
            # Fallback - create a simple circular logo placeholder
            return None
    except:
        return None

def main():
    st.set_page_config(
        page_title="Res Geo AI",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_custom_styles()
    
    # Additional styles for enhanced decorations
    st.markdown("""
    <style>
        .floating-elements {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        
        .floating-icon {
            position: absolute;
            font-size: 2rem;
            opacity: 0.1;
            animation: float 6s ease-in-out infinite;
        }
        
        
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            border-radius: 50%;
            radius: 50%;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(255, 153, 51, 0.3);
            margin-bottom: 2rem;
        }
        
        .logo-image {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border-image: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%) 1;
            box-shadow: 0 8px 32px rgba(255, 153, 51, 0.3);
            border-radius: 50%;
            margin-bottom: 1rem;
        }
        
        
        @keyframes logoGlow {
            0% { filter: drop-shadow(0 0 10px rgba(255, 153, 51, 0.5)); }
            50% { filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.5)); }
            100% { filter: drop-shadow(0 0 10px rgba(19, 136, 8, 0.5)); }
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .decorative-border {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%);
            animation: borderSlide 2s linear infinite;
        }
        
        .particle-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: #FF9933;
            border-radius: 50%;
            animation: particle 8s linear infinite;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.8);
            padding: 1.5rem;
            margin: 0.5rem;
            color: #FFFFFF;
            box-shadow: 0 4px 20px rgba(255, 153, 51, 0.2);
            border-color: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);   
            border-radius: 15px;
            text-align: center;
            background-clip: padding-box;
            position: relative;
            transition: all 0.3s ease;
        }
        
        
        .stat-card:hover {
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 10px 30px rgba(255, 153, 51, 0.4);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stat-label {
            color: #FFFFFF;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        .gradient-text {
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
    </style>
    """, unsafe_allow_html=True)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    render_home_page() if st.session_state.current_page == 'home' else render_map_page()

def render_home_page():
    # Floating background elements
    st.markdown("""
        <div class="floating-elements">
            <div class="floating-icon">🗺️</div>
            <div class="floating-icon">🌍</div>
            <div class="floating-icon">📍</div>
            <div class="floating-icon">🛰️</div>
            <div class="floating-icon">📊</div>
            <div class="floating-icon">🎯</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Logo and main content
    logo_base64 = get_base64_logo()
    
    if logo_base64:
        st.markdown(f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="Res Geo AI Logo">
                </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
                <div class="logo-container">
                    <div class="logo-image" style="display: flex; align-items: center; justify-content: center; font-size: 3rem; background: linear-gradient(135deg, #FF9933 0%, #138808 100%);">
                        🗺️
                    </div>
                </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
                <h1 class="hero-title gradient-text glow-effect">Res Geo AI</h1>
                <p class="hero-subtitle fade-in-up">A Satellite-to-Drone Dual-Modality System for Flood Detection and Victim Localization in Disaster Response</p>
                <div class="stats-container fade-in-up">
                    <div class="stat-card">
                        <div class="stat-number">28+</div>
                        <div class="stat-label">States Covered</div>
                    </div>
                    <div class="stat-card" style="animation-delay: 0.2s;">
                        <div class="stat-number">700+</div>
                        <div class="stat-label">Districts Mapped</div>
                    </div>
                    <div class="stat-card" style="animation-delay: 0.4s;">
                        <div class="stat-number">AI</div>
                        <div class="stat-label">Powered Analysis</div>
                    </div>
                </div>
                <div class="features-grid">
                    <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.1s;">
                        <div class="feature-icon">🎯</div>
                        <h3>State Analysis</h3>
                        <p>Interactive state-wise political mapping with real-time data visualization</p>
                    </div>
                    <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.2s;">
                        <div class="feature-icon">🗺️</div>
                        <h3>Tile Generation</h3>
                        <p>High-resolution map tiling system with advanced geospatial processing</p>
                    </div>
                    <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.3s;">
                        <div class="feature-icon">📊</div>
                        <h3>Data Visualization</h3>
                        <p>Advanced geospatial data insights with AI-powered analytics</p>
                    </div>
                    <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.4s;">
                        <div class="feature-icon">🛰️</div>
                        <h3>Satellite Integration</h3>
                        <p>Real-time satellite data integration for comprehensive mapping</p>
                    </div>
                    <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.5s;">
                        <div class="feature-icon">🌍</div>
                        <h3>Geographic Intelligence</h3>
                        <p>Comprehensive geographic intelligence for strategic planning</p>
                    </div>
                    <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.6s;">
                        <div class="feature-icon">📱</div>
                        <h3>Mobile Ready</h3>
                        <p>Responsive design optimized for all devices and platforms</p>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced button section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="back_btn">', unsafe_allow_html=True)
        if st.button("Launch Interactive Map", help="Access Advanced Geospatial Interface", key="back_btn"):
            st.session_state.current_page = 'map'
            st.rerun()
    
    # Footer with additional info
    st.markdown("""
        <div style="margin-top: 3rem; text-align: center; padding: 2rem; background: rgba(0,0,0,0.5); border-radius: 15px; border: 1px solid rgba(255, 153, 51, 0.3);">
            <div class="gradient-text" style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">
                🇮🇳 Proudly Made in India 🇮🇳
            </div>
            <p style="color: rgba(255,255,255,0.7); margin: 0;">
                Empowering India's geographic intelligence with cutting-edge AI technology
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()