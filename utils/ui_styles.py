import streamlit as st
from config import COLORS

def apply_custom_styles():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #4CAF50;
        animation: pulse 2s infinite;
    }
    
    .status-offline {
        background-color: #F44336;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .flood-alert {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
    }
    
    .success-alert {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
    }
    
    .detection-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #FFC107;
    }
    
    .victim-location {
        background: #ffebee;
        border: 1px solid #f44336;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #1E88E5, #42A5F5);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1E88E5, #1976D2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    st.markdown("""
    <div class="main-header">
        <h1>🛰️ Res Geo AI</h1>
        <p>Satellite-to-Drone Dual-Modality System for Flood Detection and Victim Localization</p>
    </div>
    """, unsafe_allow_html=True)

def create_metrics_cards():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center;">
                <span class="status-indicator status-online"></span>
                <span>System Status</span>
            </div>
            <h3 style="margin: 0.5rem 0; color: #4CAF50;">Online</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center;">
                <span class="status-indicator status-online"></span>
                <span>Models Loaded</span>
            </div>
            <h3 style="margin: 0.5rem 0; color: #1E88E5;">3/3</h3>
        </div>
        """, unsafe_allow_html=True)

def create_detection_card(title, content, status="info"):
    color_map = {
        "info": "#2196F3",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "danger": "#F44336"
    }
    
    st.markdown(f"""
    <div class="detection-card" style="border-left-color: {color_map.get(status, '#2196F3')};">
        <h4 style="margin: 0 0 0.5rem 0; color: {color_map.get(status, '#2196F3')};">{title}</h4>
        <p style="margin: 0;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_victim_location_card(person_id, distance, coordinates):
    st.markdown(f"""
    <div class="victim-location">
        <strong>👤 Person {person_id}</strong><br>
        📍 Distance: {distance:.0f}m from center<br>
        🌐 Coordinates: {coordinates[0]:.6f}, {coordinates[1]:.6f}
    </div>
    """, unsafe_allow_html=True)

def create_flood_alert():
    st.markdown("""
    <div class="flood-alert">
        🚨 FLOOD DETECTED - IMMEDIATE RESPONSE REQUIRED 🚨
    </div>
    """, unsafe_allow_html=True)

def create_success_alert(message):
    st.markdown(f"""
    <div class="success-alert">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)