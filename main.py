import streamlit as st
import streamlit.components.v1 as components
import os
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repository import init_db, get_users_exercises, add_exercise
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline, autoplay_audio

  
def main():
    st.set_page_config(
        page_icon="🏋️‍♀️",
        page_title="AI Real-time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered"
    )

    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    inject_local_font(os.path.join(os.getcwd(), "static", "AdobeClean.otf"), "AdobeClean")

    init_db()

    if not render_login_wall():
        return 

    initial_session_defaults()

    if "voice_pipeline" not in st.session_state:
        try:
            api_key = os.environ.get("GROQ_API_KEY", "")

            if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
            
            groq_client = Groq(api_key=api_key)
            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()
            st.session_state.voice_pipeline = VoicePipeline(llm_coach, tts)
        except Exception as e:
            st.session_state.voice_pipeline = None

    workout_started = st.session_state.get("workout_started", False)
    
    with st.sidebar:
        st.markdown("### 🏋️‍♂️ Apna AI Coach")

        username = st.session_state.get("username")
        if username:
            st.markdown(f"<div style='background: rgba(255,255,255,0.04); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px; font-size: 0.88rem;'>👤 Logged in as <strong>{username}</strong></div>", unsafe_allow_html=True)

        st.divider()

        st.markdown("#### Workout Plan")

        if not workout_started:
            plan_exercise = st.selectbox("Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")

            plan_sets = st.number_input("Sets", min_value=1, max_value=50, value=3, key="plan_sets", step=1)

            plan_reps = st.number_input("Reps per Set", min_value=1, max_value=50, value=10, key="plan_reps", step=1)

            st.markdown("")

            start_session_button = st.button("Start Workout 🚀", use_container_width=True, key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_started",
                        exercise=plan_exercise,
                        metrics={}
                    )
                    
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_complete = False
                st.rerun()
        else:
            exercise = st.session_state.get("exercise_type")
            sets = st.session_state.get("target_sets")
            reps = st.session_state.get("reps_per_set")

            st.info(f"⚡ **{exercise}**\n\nTarget: **{sets} Sets** / **{reps} Reps**")

            end_session_button = st.button("End Workout ⏹️", key="end_session_button", use_container_width=True)

            if end_session_button:
                st.session_state.workout_started = False
                
                user_id = st.session_state.get("user_id")
                total_reps = st.session_state.get("reps", 0)
                sets_completed = st.session_state.get("sets_completed", 0)
                started_at = st.session_state.get("set_cycle_started_at", time.time())
                time_taken = int(time.time() - started_at)

                if exercise and total_reps > 0:
                    add_exercise(user_id, exercise, total_reps, max(1, sets_completed), time_taken)

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics={}
                    )
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.rerun()

        if workout_started:
            st.divider()

            exercise = st.session_state.get("exercise_type")
            total_reps = st.session_state.get("reps", 0)
            current_set_reps = st.session_state.get("current_set_reps", 0)
            reps_per_set = st.session_state.get("reps_per_set", 10)
            sets_completed = st.session_state.get("sets_completed", 0)
            target_sets = st.session_state.get("target_sets", 3)

            pct_completed = min(1.0, sets_completed / target_sets) if target_sets > 0 else 0.0

            st.markdown("#### Live Workout Progress")
            
            st.markdown(f"""
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: {int(pct_completed * 100)}%;"></div>
                </div>
            """, unsafe_allow_html=True)

            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set Reps", f"{current_set_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

            st.divider()

            if exercise == "Squats":
                st.markdown("#### Squat Form Cues")
                st.metric("Knee Angle", f"{st.session_state.get('knee_angle', 0)}°")
                st.metric("Back Angle", f"{st.session_state.get('back_angle', 0)}°")
                
                depth = st.session_state.get('depth_status', 'N/A')
                pill_cls = "status-pill-success" if depth in ("GOOD DEPTH", "STANDING") else ("status-pill-error" if depth == "TOO HIGH" else "status-pill")
                st.markdown(f"<div class='status-pill {pill_cls}' style='margin-top: 8px;'><span class='pulse-dot'></span> Depth: {depth}</div>", unsafe_allow_html=True)

            elif exercise == "Push-ups":
                st.markdown("#### Push-Up Form Cues")
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}°")
                
                align = st.session_state.get('body_alignment', 'N/A')
                hip = st.session_state.get('hip_status', 'N/A')
                st.metric("Body Alignment", align)
                st.metric("Hip Position", hip)

            elif "Biceps" in str(exercise):
                st.markdown("#### Curl Form Cues")
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}°")
                
                swing = st.session_state.get('swing_status', 'N/A')
                sh = st.session_state.get('shoulder_status', 'N/A')
                st.metric("Shoulder Stability", sh)
                st.metric("Swing Detection", swing)

            elif exercise == "Shoulder Press":
                st.markdown("#### Press Form Cues")
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}°")
                st.metric("Arm Extension", st.session_state.get('extension_status', 'N/A'))
                st.metric("Back Arch", st.session_state.get('back_arch_status', 'N/A'))

            elif exercise == "Lunges":
                st.markdown("#### Lunge Form Cues")
                st.metric("Front Knee Angle", f"{st.session_state.get('front_knee_angle', 0)}°")
                st.metric("Torso Angle", f"{st.session_state.get('torso_angle', 0)}°")
                
                bal = st.session_state.get('balance_status', 'N/A')
                st.metric("Balance Status", bal)

    # --- Main Header ---
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 0.5rem;">
            <div>
                <h1 class="hero-title">APNA AI GYM COACH</h1>
                <p class="hero-subtitle">Real-time Computer Vision Pose Detection & Proactive AI Voice Coaching</p>
            </div>
            <div>
                <span class="status-pill status-pill-success">
                    <span class="pulse-dot"></span> AI SENSOR ACTIVE
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
 
    if st.session_state.get("audio_to_play"):
        autoplay_audio(st.session_state.audio_to_play)

    feedback = st.session_state.get("coach_feedback")
    if feedback:
        st.markdown(f"""
            <div class="ai-coach-card">
                <div class="ai-coach-avatar">🤖</div>
                <div class="ai-coach-text">
                    <strong style="color: var(--primary-cyan); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 2px;">Apna AI Voice Coach</strong>
                    "{feedback}"
                </div>
            </div>
        """, unsafe_allow_html=True)

    if not workout_started:
        st.markdown(
            """
            <div class="welcome-card">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #00F2FE 0%, #3B82F6 100%); box-shadow: 0 0 20px rgba(0, 242, 254, 0.4); font-size: 2rem; margin-bottom: 1rem;">
                    🎯
                </div>
                <h2 style="margin-bottom: 8px;">Set Up Your Workout Plan</h2>
                <p style="color: var(--text-secondary); max-width: 540px; margin: 0 auto 1.25rem auto;">
                    Select your target exercise, sets, and reps in the sidebar menu, then click <strong>Start Workout</strong> to activate live AI camera tracking and voice coaching.
                </p>
                <div class="step-badges">
                    <div class="step-badge">1️⃣ Select Exercise</div>
                    <div class="step-badge">2️⃣ Set Target Sets & Reps</div>
                    <div class="step-badge">3️⃣ Start AI Coach 🚀</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

        inject_webrtc_styles()

    st.divider()

    st.markdown("### 📊 Workout History & Analytics")

    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username")
    history_rows = get_users_exercises(user_id, username)

    if history_rows:
        arr = [
            {
                "Exercise": row['exercise_name'],
                "Reps": row['reps'],
                "Sets": row['sets'],
                "Time (sec)": row['time'],
                "Date": row['created_at']
            }
            for row in history_rows
        ]

        df = pd.DataFrame(arr)

        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            agg_df = df.groupby(["Exercise", "Date"]).agg({
                "Reps": 'sum',
                "Sets": "sum",
                "Time (sec)": "sum"
            }).reset_index()
            agg_df.index += 1
            st.table(agg_df, border="horizontal")
        else:
            st.info("No workout history found yet. Complete a workout to see your stats here!")
    else:
        st.info("No workout history found yet. Complete a workout to see your stats here!")


if __name__ == "__main__":
    main()