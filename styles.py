import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        .stApp {
            background: #000000;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: background-color 0.1s ease;
        }
        
        .hero-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 70vh;
            text-align: center;
            padding: 2rem;
            along-items: center;
            width: 100%;
        }
        
        .hero-content {
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 40px;
            padding: 0.5rem;
            align-items: center;
            display: flex;
            flex-direction: column;
            box-shadow: 0 8px 32px rgba(255, 153, 51, 0.3);
            border: 3px solid;
            border-image: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%) 1;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
            width: 100%;
        }
        
        .hero-content:hover {
            box-shadow: 0 12px 40px rgba(255, 153, 51, 0.5);
            transform: translateY(-5px);
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: #FFFFFF;
            margin-bottom: 2rem;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .feature-card {
            background: rgba(0, 0, 0, 0.7);
            padding: 1.5rem;
            border-radius: 15px;
            border: 2px solid;
            border-image: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%) 1;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 10px 30px rgba(255, 153, 51, 0.4);
        }
        
        .feature-card:hover::before {
            opacity: 0.1;
        }
        
        .feature-card h3 {
            color: #FFFFFF;
            margin-bottom: 0.5rem;
        }
        
        .feature-card p {
            color: rgba(255, 255, 255, 0.8);
            margin: 0;
        }
        
        .control-panel {
            background: rgba(0, 0, 0, 0.9);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            color: white;
            border: 2px solid;
            border-image: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%) 1;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            color: white;
            border: 2px solid #FFFFFF;
            border-radius: 25px;
            padding: 0.8rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 153, 51, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(255, 153, 51, 0.5);
            background: linear-gradient(135deg, #138808 0%, #FF9933 100%);
            border-color: #FF9933;
        }
    
        
        .stButton > button:active {
            transform: translateY(-1px);
            background: linear-gradient(135deg, #FFFFFF 0%, #FF9933 50%, #138808 100%);
            color: #000000;
        }
        
        .tile-info {
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 950;
            background: rgba(0, 0, 0, 0.8);
            color: #FFFFFF;
            border: 3px solid;
            border-image: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%) 1;
            transition: all 0.3s ease;
        }
        
        .tile-info:hover {
            box-shadow: 0 5px 20px rgba(255, 153, 51, 0.4);
            transform: translateY(-2px);
        }
        
        .back-button {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
        }
        
        
        /* Additional Indian Flag themed elements */
        .indian-flag-divider {
            height: 4px;
            background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%);
            margin: 1rem 0;
            border-radius: 2px;
        }
        
        .patriotic-glow {
            animation: patrioticGlow 3s ease-in-out infinite alternate;
        }
        
        @keyframes patrioticGlow {
            0% {
                box-shadow: 0 0 20px rgba(255, 153, 51, 0.5);
            }
            50% {
                box-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
            }
            100% {
                box-shadow: 0 0 20px rgba(19, 136, 8, 0.5);
            }
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: #000000;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            border-radius: 6px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #138808 0%, #FF9933 100%);
        }
    </style>
    """, unsafe_allow_html=True)