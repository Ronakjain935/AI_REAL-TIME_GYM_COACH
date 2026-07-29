from jinja2 import defaults
import streamlit as st
def initial_session_default():
    defaults={
        "reps":0,
        "target_sets":0,
        "reps_per_set":0,
        "sets_completed":0,
        "current_sets_reps":0,
        "workout_complete":False,
        "last_notified_sets_completed":0,
        "last_notified_workout_completed":False,
        "last_saved_sets_completed":0,
        "set_cycle_started_at":0.0,
        "last_exercise_type":"Squats",

        # Welcome plan(set before starting)
        "workout_started":False,
        "plan_exercise":"Squats",
        "plan_sets": 3,
        "plan_reps": 10,

        # Common Angles
        "knee_angle": 0,
        "back_angle": 0,
        "elbow_angle": 0,
        "front_knee_angle": 0,
        "torso_angle": 0,

        # Status fields
        "depth_status": "N/A",
        "body_alignment": "N/A",
        "body_alingment": "N/A",
        "hip_position": "N/A",
        "hip_status": "N/A",
        "shoulder_status": "N/A",
        "swing_status": "N/A",
        "extension_status": "N/A",
        "back_arch_status": "N/A",
        "balance_status": "N/A",

    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value