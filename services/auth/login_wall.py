import streamlit as st 
from services.persistence.exercise_repository import get_or_create_user

def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
        
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, #00F2FE 0%, #3B82F6 100%); box-shadow: 0 0 24px rgba(0,242,254,0.4); font-size: 2.2rem; margin-bottom: 1rem;">
                🏋️‍♂️
            </div>
            <h1 class="hero-title">APNA AI GYM COACH</h1>
            <p class="hero-subtitle">Real-time Computer Vision Pose Analysis & Proactive Voice Coaching</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        st.markdown("<h3 style='margin-bottom: 0.5rem; text-align: center;'>Welcome Athlete</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-secondary); text-align: center; font-size: 0.9rem; margin-bottom: 1.5rem;'>Enter your username to access your personal AI training dashboard.</p>", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="e.g. RonakJain")
        submit_button = st.form_submit_button("Launch Gym Dashboard ⚡", width="stretch")
        
        if submit_button:
            if not username.strip():
                st.error("Please enter a valid username to continue.")
                return False
            user = get_or_create_user(username.strip())
            st.session_state["username"] = user["username"]
            st.session_state["user_id"] = user["id"]
            st.rerun()

    return False
