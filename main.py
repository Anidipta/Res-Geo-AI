import streamlit as st
import base64
from pathlib import Path
from styles import apply_custom_styles
from map import render_map_page
from components import flood
from victim import render_victim_page

flood.initialize_flood_model()

def get_base64_logo():
    try:
        logo_path = Path("src/images/LOGO_ResGeoAI.png")
        if logo_path.exists():
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        else:
            return None
    except:
        return None

def create_custom_tabs():
    st.markdown("""
    <style>
        .custom-tabs {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0, 0, 0, 0.95);
            padding: 1rem 2rem;
            border-radius: 25px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(255, 153, 51, 0.3);
            border: 2px solid;
            border-image: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%) 1;
            backdrop-filter: blur(15px);
        }
        
        .left-tabs, .right-tabs {
            display: flex;
            gap: 1rem;
        }
        
        .tab-button {
            background: linear-gradient(135deg, rgba(255, 153, 51, 0.1) 0%, rgba(19, 136, 8, 0.1) 100%);
            color: #FFFFFF;
            border: 2px solid rgba(255, 153, 51, 0.3);
            border-radius: 20px;
            padding: 0.8rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            position: relative;
            overflow: hidden;
        }
        
        .tab-button:hover {
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 153, 51, 0.4);
            border-color: #FFFFFF;
        }
        
        .tab-button.active {
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            box-shadow: 0 6px 20px rgba(255, 153, 51, 0.5);
            border-color: #FFFFFF;
            transform: translateY(-2px);
        }
        
        .logo-tab {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            align-self: center;
            justify-content: center;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .tab-icon {
            font-size: 1.2rem;
        }
        
        .stButton {
            background: transparent;
            border: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            align-items: center;
            display: flex;
            justify-content: center;
            padding: 0;
            cursor: pointer;
            
        }
    </style>
    """, unsafe_allow_html=True)
    
    logo_base64 = get_base64_logo()
    logo_display = f'<img src="data:image/png;base64,{logo_base64}" style="width: 40px; height: 40px; border-radius: 50%;">' if logo_base64 else '🗺️'
    
    # col1, col2, col3 = st.columns([2, 3, 2])
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    with col1:
        home_active = "active" if st.session_state.get('current_tab', 'HOME') == 'HOME' else ""
        if st.button("HOME", key="home_btn", help="Navigate to Home"):
            st.session_state.current_tab = 'HOME'
            st.rerun()
        
    with col2:
        solution_active = "active" if st.session_state.get('current_tab', 'HOME') == 'SOLUTION' else ""
        if st.button("LIVE", key="solution_btn", help="Access Solutions"):
            st.session_state.current_tab = 'SOLUTION'
            st.rerun()
    
    with col3:
        st.markdown(f"""
        <div class="logo-container">
                            <img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="Res Geo AI Logo">
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        demo_active = "active" if st.session_state.get('current_tab', 'HOME') == 'DEMO' else ""
        
        if st.button("UAV", key="demo_btn", help="View Demonstrations"):
            st.session_state.current_tab = 'DEMO'
            st.rerun()
    with col5:
        about_active = "active" if st.session_state.get('current_tab', 'HOME') == 'ABOUT' else ""
        
        if st.button("ABOUT", key="about_btn", help="About Developer"):
            st.session_state.current_tab = 'ABOUT'
            st.rerun()

def render_home_page():
    st.markdown("""
        <div class="floating-elements">
            <div class="floating-icon" style="top: 10%; left: 5%; animation-delay: 0s;">🗺️</div>
            <div class="floating-icon" style="top: 20%; right: 10%; animation-delay: 1s;">🌍</div>
            <div class="floating-icon" style="top: 60%; left: 8%; animation-delay: 2s;">📍</div>
            <div class="floating-icon" style="top: 40%; right: 15%; animation-delay: 3s;">🛰️</div>
            <div class="floating-icon" style="top: 70%; left: 20%; animation-delay: 4s;">📊</div>
            <div class="floating-icon" style="top: 30%; right: 5%; animation-delay: 5s;">🎯</div>
        </div>
    """, unsafe_allow_html=True)
    
    logo_base64 = get_base64_logo()
    
    if logo_base64:
        st.markdown(f"""
                <div>
                    <div>
                    <h1 class="hero-title gradient-text">Res Geo AI</h1>
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
                            <div class="stat-card" style="animation-delay: 0.6s;">
                                <div class="stat-number">24/7</div>
                                <div class="stat-label">Real-time Monitoring</div>
                            </div>
                        </div>
                        <div class="features-grid">
                            <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.1s;">
                                <div class="feature-icon">🎯</div>
                                <h3>Precision Mapping</h3>
                                <p>Advanced geospatial analysis with centimeter-level accuracy for disaster response planning</p>
                            </div>
                            <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.2s;">
                                <div class="feature-icon">🗺️</div>
                                <h3>Smart Tile Generation</h3>
                                <p>Intelligent map tiling with adaptive resolution and real-time processing capabilities</p>
                            </div>
                            <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.4s;">
                                <div class="feature-icon">🛰️</div>
                                <h3>Dual-Modal Detection</h3>
                                <p>Seamless integration of satellite imagery and drone surveillance for comprehensive coverage</p>
                            </div>
                            <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.5s;">
                                <div class="feature-icon">🌊</div>
                                <h3>Flood Intelligence</h3>
                                <p>Real-time flood detection with victim localization using advanced computer vision algorithms</p>
                            </div>
                            <div class="feature-card glow-effect fade-in-up" style="animation-delay: 0.6s;">
                                <div class="feature-icon">⚡</div>
                                <h3>Rapid Response</h3>
                                <p>Instant alert system with automated emergency response coordination and resource allocation</p>
                            </div>
                        </div>
                    </div>
                </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="cta-section">
            <div class="indian-flag-divider"></div>
            <div class="patriotic-container">
                <div class="gradient-text" style="font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; text-align: center;">
                    🇮🇳 Empowering India's Disaster Preparedness 🇮🇳
                </div>
                <p style="color: rgba(255,255,255,0.8); text-align: center; font-size: 1.1rem; margin-bottom: 2rem;">
                    Leveraging cutting-edge AI and geospatial technology to protect communities and save lives across the nation
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_solution_page():
    st.markdown("""
        <div class="solution-header">
            <h1 class="page-title gradient-text">🚀 Advanced Solutions</h1>
            <p class="page-subtitle">Cutting-edge technology for disaster management and response</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1, 2,1,2 ,1])
    with col2:
        st.markdown('<div class="launch-section">', unsafe_allow_html=True)
        if st.button("🗺️ Launch Satellite Map", help="Access Advanced Geospatial Interface", key="map_launch"):
            st.session_state.current_tab = 'MAP'
            render_map_page()
            st.rerun()
    
    with col4:
        st.markdown('<div class="launch-section">', unsafe_allow_html=True)
        if st.button("📍 Launch Victim Finder", help="Access Victim Localization Interface", key="victim_finder_launch"):
            st.session_state.current_tab = 'VICTIM'
            render_victim_page()
            st.rerun()
            
    st.markdown("""
        <div class="solution-grid">
            <div class="solution-card">
                <div class="solution-icon">🛰️</div>
                <h3>Satellite Monitoring</h3>
                <p>Real-time satellite data processing with AI-powered flood detection algorithms</p>
                <div class="tech-stack">
                    <span class="tech-tag">Computer Vision</span>
                    <span class="tech-tag">Remote Sensing</span>
                    <span class="tech-tag">Deep Learning</span>
                </div>
            </div>
            <div class="solution-card">
                <div class="solution-icon">👁️‍🗨️</div>
                <h3>Fine Integrated Detection</h3>
                <p>Autonomous fined surveillance with victim detection and rescue coordination</p>
                <div class="tech-stack">
                    <span class="tech-tag">Object Detection</span>
                    <span class="tech-tag">Path Planning</span>
                    <span class="tech-tag">Real-time Processing</span>
                </div>
            </div>
            <div class="solution-card">
                <div class="solution-icon">🧠</div>
                <h3>AI-Powered Analytics</h3>
                <p>Machine learning models for predictive analysis and risk assessment</p>
                <div class="tech-stack">
                    <span class="tech-tag">Neural Networks</span>
                    <span class="tech-tag">Predictive Modeling</span>
                    <span class="tech-tag">Data Mining</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_demo_page():
    st.markdown("""
        <div class="demo-header">
            <h1 class="page-title gradient-text">🎮 Live Demonstrations</h1>
            <p class="page-subtitle">Experience our technology in action</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="demo-container">
            <div class="demo-placeholder">
                <div class="demo-icon">🚧</div>
                <h2>Coming Soon</h2>
                <p>Interactive demos and live simulations will be available here</p>
                <div class="demo-features">
                    <div class="demo-feature">
                        <span class="demo-feature-icon">🎥</span>
                        <span>Live Satellite Feed Simulation</span>
                    </div>
                    <div class="demo-feature">
                        <span class="demo-feature-icon">🎯</span>
                        <span>Flood Detection Algorithm Demo</span>
                    </div>
                    <div class="demo-feature">
                        <span class="demo-feature-icon">📱</span>
                        <span>Mobile App Interface Preview</span>
                    </div>
                    <div class="demo-feature">
                        <span class="demo-feature-icon">🗺️</span>
                        <span>Interactive Map Walkthrough</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_about_page():
    st.markdown("""
        <div class="about-header">
            <h1 class="page-title gradient-text">About Developer</h1>
            <p class="page-subtitle">Meet the mind behind Res Geo AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="developer-profile">
            <div class="profile-card">
                <div class="profile-avatar">
                    <img
                        src="https://api.dicebear.com/9.x/personas/svg?seed=Kingston&backgroundType[]&facialHairProbability=0&hair=bobBangs,bobCut,bunUndercut,buzzcut,cap,curly,curlyBun,curlyHighTop,extraLong,fade,long,mohawk,pigtails,shortCombover,shortComboverChops,sideShave,straightBun&mouth=bigSmile,smile,smirk,surprise"
                        alt="avatar" width="110" height="110">
                </div>
                <div class="profile-info">
                    <h2 class="developer-name gradient-text">Anidipta Pal</h2>
                    <p class="developer-title">AI Engineer & Computer Vision Engineer</p>
                    <div class="bio-section">
                        <p>Passionate about leveraging artificial intelligence and geospatial technology to solve real-world problems. Specialized in computer vision, machine learning, and disaster management systems.</p>
                    </div>
                    <div class="skills-section">
                        <h3>Technical Expertise</h3>
                        <div class="skills-grid">
                            <div class="skill-item">
                                <span class="skill-icon">🤖</span>
                                <span>Machine Learning</span>
                            </div>
                            <div class="skill-item">
                                <span class="skill-icon">👁️</span>
                                <span>Computer Vision</span>
                            </div>
                            <div class="skill-item">
                                <span class="skill-icon">🗺️</span>
                                <span>GIS & Remote Sensing</span>
                            </div>
                            <div class="skill-item">
                                <span class="skill-icon">🐍</span>
                                <span>Python & AI Frameworks</span>
                            </div>
                            <div class="skill-item">
                                <span class="skill-icon">📊</span>
                                <span>Data Science</span>
                            </div>
                        </div>
                    </div>
                    <div class="mission-section">
                        <h3>Mission</h3>
                        <p>"To harness the power of AI and geospatial technology in creating solutions that protect communities and save lives during natural disasters."</p>
                    </div>
                    <div class="contact-section">
                        <h3>Connect</h3>
                        <div class="contact-links">
                            <div class="contact-item">
                                <span class="contact-icon">📧</span>
                                <span>Available for collaboration</span>
                            </div>
                            <div class="contact-item">
                                <span class="contact-icon">🌐</span>
                                <span>Open source contributor</span>
                            </div>
                            <div class="contact-item">
                                <span class="contact-icon">🚀</span>
                                <span>Innovation enthusiast</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Res Geo AI - Advanced Disaster Response System",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_custom_styles()
    
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'HOME'
    
    create_custom_tabs()
    
    if st.session_state.current_tab == 'HOME':
        render_home_page()
    elif st.session_state.current_tab == 'SOLUTION':
        render_solution_page()
    elif st.session_state.current_tab == 'DEMO':
        render_demo_page()
    elif st.session_state.current_tab == 'ABOUT':
        render_about_page()
    elif st.session_state.current_tab == 'MAP':
        render_map_page()
    elif st.session_state.current_tab == 'VICTIM':
        render_victim_page()

if __name__ == "__main__":
    main()