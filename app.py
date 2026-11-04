import streamlit as st
from modules.auth import check_login, logout
import os

st.set_page_config(page_title="EV Intelligence App", page_icon="⚡", layout="wide")

# This completely hides the top toolbar and Deploy button
st.set_option("client.toolbarMode", "viewer")

# Triggers secure SQLite login and hides sidebar until authenticated
if check_login():
    if os.path.exists("static/logo.png"):
        st.sidebar.image("static/logo.png", width=220)
        
    st.sidebar.success(f"Welcome, {st.session_state.get('name', 'User')}!")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    # --- MAIN LANDING DASHBOARD ---
    st.title("⚡ EV Range Prediction & Intelligence Dashboard")
    st.markdown("Connected to **SQLite Database** & Live APIs. Use the sidebar links to navigate to **Live Route Prediction** and **Interactive Route Map**.")

    st.markdown("---")

    # The 3 Clean Summary Boxes Explaining App Features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🗺️ Live Routing & Weather")
        st.markdown("Integrates **OSRM** for precise highway routing and **Open-Meteo** for real-time temperature and wind telemetry along your journey.")

    with col2:
        st.markdown("### ⚡ Real Charging Hubs")
        st.markdown("Queries the live **Overpass API** to discover real-world charging stations dynamically customized to whatever destination you enter.")

    with col3:
        st.markdown("### 📊 ML Range Prediction")
        st.markdown("Predicts precise energy drain using machine learning models, taking vehicle load, passenger weight, terrain, and driving modes into account.")

    st.markdown("---")
    st.info("💡 **Quick Start:** Click on **Live Prediction** in the sidebar to begin testing your route parameters!")

