from streamlit import subheader
import streamlit as st
from services.auth.login_wall import render_login_wall
from services.state.session_default import  initial_session_default
from services.config.workout_config import EXERCISE_OPTION
import os
from services.ui.style_loader import load_css, inject_local_font
from services.persistence.exercise_repository import init_db

def main():
    st.set_page_config(
        page_icon="💪",
        page_title="AI REAL-TIME GYM COACH",
        initial_sidebar_state="expanded",
        layout="centered"

    )
    base_dir = os.path.dirname(os.path.abspath(__file__))
    load_css(os.path.join(base_dir, "static", "style.css"))
    inject_local_font(os.path.join(base_dir, "static", "AdobeClean.otf"), "AdobeClean")
    
    init_db()


    if not render_login_wall():
        return
    initial_session_default()

    workout_started=st.session_state.get("workout_started")

    with st.sidebar:
        st.title("Apna Ai Coach")
        if st.session_state.get("username"):
            st.caption(f"Login as {st.session_state.get('username')}")
        st.divider()

        st.subheader("Workout plan")

        if not workout_started:
            st.selectbox("Exercise", options=EXERCISE_OPTION, key="plan_exercise")
            st.number_input("sets",min_value=0,max_value=50,key="plan_sets",step=1)
            st.number_input("Reps per Set",min_value=0,max_value=50,key="plan_reps",step=1)
            st.markdown("")
            start_session_button = st.button("Start Session", use_container_width=True, key="start_session_btn")
            if start_session_button:
                st.session_state["workout_started"] = True
                st.rerun()
        else:
            exercise = st.session_state.get("plan_exercise")
            sets = st.session_state.get("plan_sets")
            reps = st.session_state.get("plan_reps")
            st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")
            end_session_button = st.button("End Session", key="end_session_button", use_container_width=True)
            if end_session_button:
                st.session_state["workout_started"] = False
                st.rerun()

        if workout_started:
            st.divider()
            exercise = st.session_state.get("plan_exercise")
            total_reps = st.session_state.get("reps", 0)
            reps_per_set = st.session_state.get("plan_reps", 0)
            current_sets_reps = st.session_state.get("current_sets_reps", 0)
            sets_completed = st.session_state.get("sets_completed", 0)
            target_sets = st.session_state.get("plan_sets", 0)
            st.subheader("Progress")
            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set Reps", f"{current_sets_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squats Metrics")
                st.metric("Knee Angle", f"{st.session_state.get('knee_angle', 0)}")
                st.metric("Back Angle", f"{st.session_state.get('back_angle', 0)}")
                st.metric("Depth Status", f"{st.session_state.get('depth_status', 'N/A')}")
            
            elif exercise == "Push-ups":
                st.subheader("Push-ups Metrics")
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}")
                st.metric("Body Alignment", f"{st.session_state.get('body_alignment', st.session_state.get('body_alingment', 'N/A'))}")
                st.metric("Hip Position", f"{st.session_state.get('hip_position', st.session_state.get('hip_status', 'N/A'))}")

            elif exercise == "Biceps Curls (Dumbell)":
                st.subheader("Biceps Curls (Dumbell) Metrics")
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}")
                st.metric("Shoulder Stability", f"{st.session_state.get('shoulder_status', 'N/A')}")
                st.metric("Swing Detection", f"{st.session_state.get('swing_status', 'N/A')}")
            
            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}")
                st.metric("Arm Extension", f"{st.session_state.get('extension_status', 'N/A')}")
                st.metric("Back Arch", f"{st.session_state.get('back_arch_status', 'N/A')}")

            elif exercise == "Lunges":
                st.subheader("Lunges Metrics")
                st.metric("Front Knee Angle", f"{st.session_state.get('front_knee_angle', 0)}")
                st.metric("Torso Angle", f"{st.session_state.get('torso_angle', 0)}")
                st.metric("Balance Status", f"{st.session_state.get('balance_status', 'N/A')}")
            
if __name__ == "__main__":
    main()

