import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: all 0.3s ease;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, rgba(255, 153, 51, 0.1) 0%, rgba(19, 136, 8, 0.1) 100%);
            color: #FFFFFF;
            border: 2px solid rgba(255, 153, 51, 0.3);
            border-radius: 20px;
            padding: 0.8rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 153, 51, 0.4);
            border-color: #FFFFFF;
        }
        
        .floating-elements {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        }
        
        .floating-icon {
            position: absolute;
            font-size: 2.5rem;
            opacity: 0.08;
            animation: float 8s ease-in-out infinite;
            filter: blur(1px);
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(5deg); }
        }
        
        .hero-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
            text-align: center;
            padding: 2rem;
            width: 100%;
        }
        
        .hero-content {
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 3rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 20px 60px rgba(255, 153, 51, 0.2);
            border: 3px solid transparent;
            background-clip: padding-box;
            position: relative;
            transition: all 0.3s ease;
            width: 100%;
            max-width: 1200px;
        }
        
        .hero-content::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 30px;
            padding: 3px;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            z-index: -1;
        }
        
        .hero-content:hover {
            box-shadow: 0 25px 80px rgba(255, 153, 51, 0.3);
            transform: translateY(-5px);
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
            position: relative;
        }
        
        .logo-image {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            border: 4px solid;
            box-shadow: 0 15px 40px rgba(255, 153, 51, 0.4);
            animation: logoGlow 4s ease-in-out infinite;
            transition: all 0.3s ease;
        }
        
        .logo-image:hover {
            transform: scale(1.1);
            box-shadow: 0 20px 50px rgba(255, 153, 51, 0.6);
        }
        
        @keyframes logoGlow {
            0% { filter: drop-shadow(0 0 15px rgba(255, 153, 51, 0.5)); }
            50% { filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.5)); }
            100% { filter: drop-shadow(0 0 15px rgba(19, 136, 8, 0.5)); }
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1.5rem;
            align-self: center;
            text-align: center;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
            letter-spacing: -1px;
        }
        
        .hero-subtitle {
            font-size: 1.4rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 3rem;
            align-self: center;
            justify-self: center;
            text-align: center;
            line-height: 1.6;
            max-width: 800px;
            font-weight: 400;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 3rem 0;
            width: 100%;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.9);
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            position: relative;
            transition: all 0.4s ease;
            border: 2px solid transparent;
            background-clip: padding-box;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 20px;
            padding: 2px;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            z-index: -1;
        }
        
        .stat-card:hover {
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 20px 40px rgba(255, 153, 51, 0.4);
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1rem;
            font-weight: 500;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 5rem 0;
            width: 100%;
            align-items: center;
            justify-items: center;
        }
        
        .feature-card {
            background: rgba(0, 0, 0, 0.85);
            padding: 2.5rem;
            border-radius: 20px;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            border: 2px solid transparent;
            background-clip: padding-box;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 20px;
            padding: 2px;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            z-index: -1;
            opacity: 0.5;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 50px rgba(255, 153, 51, 0.3);
        }
        
        .feature-card:hover::before {
            opacity: 1;
        }
        
        .feature-icon {
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            filter: drop-shadow(0 4px 8px rgba(255, 153, 51, 0.3));
        }
        
        .feature-card:hover .feature-icon {
            transform: scale(1.1);
            filter: drop-shadow(0 6px 12px rgba(255, 153, 51, 0.5));
        }
        
        .feature-card h3 {
            color: #FFFFFF;
            margin-bottom: 1rem;
            font-size: 1.4rem;
            font-weight: 600;
        }
        
        .feature-card p {
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.6;
            font-size: 1rem;
        }
        
        .gradient-text {
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .indian-flag-divider {
            height: 6px;
            background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%);
            margin: 3rem 0;
            border-radius: 3px;
            box-shadow: 0 4px 12px rgba(255, 153, 51, 0.3);
        }
        
        .cta-section {
            background: rgba(0, 0, 0, 0.8);
            padding: 3rem;
            border-radius: 25px;
            margin-top: 3rem;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
        }
        
        .cta-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 25px;
            padding: 2px;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            z-index: -1;
        }
        
        .page-title {
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
        }
        
        .page-subtitle {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.8);
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .solution-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .solution-card {
            background: rgba(0, 0, 0, 0.9);
            padding: 2.5rem;
            border-radius: 20px;
            transition: all 0.4s ease;
            position: relative;
            border: 2px solid transparent;
            background-clip: padding-box;
        }
        
        .solution-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 20px;
            padding: 2px;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            z-index: -1;
        }
        
        .solution-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(255, 153, 51, 0.3);
        }
        
        .solution-icon {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .solution-card h3 {
            color: #FFFFFF;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .solution-card p {
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .tech-tag {
            background: linear-gradient(135deg, rgba(255, 153, 51, 0.2) 0%, rgba(19, 136, 8, 0.2) 100%);
            color: #FFFFFF;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            border: 1px solid rgba(255, 153, 51, 0.3);
            transition: all 0.3s ease;
        }
        
        .tech-tag:hover {
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            transform: translateY(-2px);
        }
        
        .launch-section {
            text-align: center;
            margin: 3rem 0;
        }
        
        .demo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 60vh;
            padding: 2rem;
        }
        
        .demo-placeholder {
            background: rgba(0, 0, 0, 0.9);
            padding: 4rem;
            border-radius: 30px;
            text-align: center;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
            max-width: 600px;
        }
        
        .demo-placeholder::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 30px;
            padding: 2px;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            z-index: -1;
        }
        
        .demo-icon {
            font-size: 5rem;
            margin-bottom: 2rem;
            opacity: 0.7;
        }
        
        .demo-placeholder h2 {
            color: #FFFFFF;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .demo-placeholder p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        
        .demo-features {
            display: grid;
            gap: 1rem;
            text-align: left;
        }
        
        .demo-feature {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(255, 153, 51, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(255, 153, 51, 0.3);
            transition: all 0.3s ease;
        }
        
        .demo-feature:hover {
            background: rgba(255, 153, 51, 0.2);
            transform: translateX(5px);
        }
        
        .demo-feature-icon {
            font-size: 1.5rem;
        }
        
        .demo-feature span:last-child {
            color: #FFFFFF;
            font-weight: 500;
        }
        
        .developer-profile {
            display: flex;
            justify-content: center;
            padding: 2rem;
        }
        
        .profile-card {
            background: rgba(0, 0, 0, 0.9);
            padding: 3rem;
            border-radius: 30px;
            max-width: 800px;
            width: 100%;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
        }
        
        .profile-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 30px;
            padding: 2px;
            background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            z-index: -1;
        }
        
        .profile-avatar {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .profile-avatar svg {
            filter: drop-shadow(0 8px 16px rgba(255, 153, 51, 0.3));
            transition: all 0.3s ease;
        }
        
        .profile-avatar:hover svg {
            transform: scale(1.05);
            filter: drop-shadow(0 12px 24px rgba(255, 153, 51, 0.5));
        }
        
        .developer-name {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .developer-title {
            font-size: 1.3rem;
            color: rgba(255, 255, 255, 0.8);
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 500;
        }
        
        .bio-section {
            margin-bottom: 2rem;
        }
        
        .bio-section p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            line-height: 1.6;
            text-align: center;
        }
        
        .skills-section, .mission-section, .contact-section {
            margin-bottom: 2rem;
        }
        
        .skills-section h3, .mission-section h3, .contact-section h3 {
            color: #FFFFFF;
            font-size: 1.4rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .skill-item {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 1rem;
            background: rgba(255, 153, 51, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(255, 153, 51, 0.3);
            transition: all 0.3s ease;
        }
        
        .skill-item:hover {
            background: rgba(255, 153, 51, 0.2);
            transform: translateY(-2px);
        }
        
        .skill-icon {
            font-size: 1.5rem;
        }
        
        .skill-item span:last-child {
            color: #FFFFFF;
            font-weight: 500;
        }
        
        .mission-section p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            line-height: 1.6;
            font-style: italic;
            text-align: center;
            padding: 1.5rem;
            background: rgba(255, 153, 51, 0.05);
            border-radius: 15px;
            border-left: 4px solid #FF9933;
        }
        
        .contact-links {
            display: grid;
            gap: 1rem;
        }
        
        .contact-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(19, 136, 8, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(19, 136, 8, 0.3);
            transition: all 0.3s ease;
        }
        
        .contact-item:hover {
            background: rgba(19, 136, 8, 0.2);
            transform: translateX(5px);
        }
        
        .contact-icon {
            font-size: 1.5rem;
        }
        
        .contact-item span:last-child {
            color: #FFFFFF;
            font-weight: 500;
        }
        
        .fade-in-up {
            animation: fadeInUp 0.8s ease-out forwards;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .glow-effect {
            transition: all 0.3s ease;
        }
        
        .glow-effect:hover {
            filter: drop-shadow(0 0 20px rgba(255, 153, 51, 0.4));
        }
        
        ::-webkit-scrollbar {
            width: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.5);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
            border-radius: 6px;
            border: 2px solid transparent;
            background-clip: padding-box;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #138808 0%, #FF9933 100%);
        }
        
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .hero-subtitle {
                font-size: 1.1rem;
            }
            
            .stats-container {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
            
            .logo-image {
                width: 100px;
                height: 100px;
            }
            
            .page-title {
                font-size: 2rem;
            }
            
            .solution-grid {
                grid-template-columns: 1fr;
            }
            
            .skills-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """, unsafe_allow_html=True)