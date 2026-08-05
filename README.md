# 🏋️‍♂️ AI Real-Time Gym Coach

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0%2B-FF4B4B?logo=streamlit&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-0097A7?logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Headless-5C3EE8?logo=opencv&logoColor=white)
![Groq AI](https://img.shields.io/badge/Groq%20AI-LLaMA3-f34f29?logo=ai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An interactive, AI-powered real-time fitness coaching platform. Powered by **MediaPipe Pose**, **OpenCV**, **Streamlit WebRTC**, **Groq LLM**, and **gTTS**, this application tracks human movement through a webcam, analyzes posture & body joint angles in real time, auto-counts reps, and delivers real-time voice feedback to optimize workout form.

---

## ✨ Key Features

- 📹 **Real-Time WebRTC Pose Tracking**: Low-latency video streaming directly in your web browser via `streamlit-webrtc`.
- 📐 **Biomechanical Angle Analysis**: Accurate joint coordinate & angle calculations using MediaPipe Pose Landmarks.
- 🏋️ **Supported Exercises**:
  - 🦾 **Biceps Curls**: Tracks elbow flexion, extension, swing detection, and repetition cycles.
  - 🏋️‍♂️ **Squats**: Detects knee angle, depth status (*GOOD DEPTH* vs *TOO HIGH*), and back alignment.
  - 🧘 **Push-Ups**: Monitors chest-to-ground distance, arm bend angle, body alignment, and repetition stages.
  - 🏋️‍♀️ **Shoulder Press**: Tracks overhead arm extension, back arching, and press range of motion.
  - 🦵 **Lunges**: Evaluates lead knee flexion, torso angle, and balance status.
- 🗣️ **AI Voice Coach & LLM Guidance**: Integrates **Groq AI (LLaMA 3)** for personalized coaching commentary and **gTTS** for text-to-speech audio feedback upon set completions or form anomalies.
- 📊 **Progress & Analytics Dashboard**: Built-in SQLite database (`data.db`) logs completed workouts, total sets, reps, and timestamped history per user.
- 🔐 **User Authentication**: Simple login system supporting individual user progress tracking.
- 🎨 **Modern Dark UI**: Customized CSS theme, responsive video overlay, and real-time visual HUD.

---

## 🛠️ Tech Stack

| Domain | Technologies Used |
| :--- | :--- |
| **Frontend & Web Framework** | [Streamlit](https://streamlit.io/), HTML5, Custom CSS |
| **Computer Vision & Kinematics** | [MediaPipe Pose](https://mediapipe.dev/), [OpenCV](https://opencv.org/) |
| **Real-Time Video Stream** | [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc), `av` (PyAV) |
| **AI Intelligence & Voice** | [Groq Cloud API](https://groq.com/) (LLaMA 3), [gTTS](https://pypi.org/project/gTTS/) |
| **Database & Persistence** | SQLite (`sqlite3`), Pandas |
---

## 📂 Project Architecture

```
AI_REAL-TIME_GYM_COACH/
├── core/                       # Base class abstractions for exercises
│   └── base_exercise.py
├── detectors/                  # Exercise-specific pose detection logic
│   ├── biceps_curl.py
│   ├── squats.py
│   ├── pushup.py
│   ├── shoulder_press.py
│   └── lunges.py
├── services/                   # Business logic, services & modules
│   ├── auth/                   # Authentication & user login wall
│   ├── coaching/               # Groq LLM integration, gTTS & Voice pipeline
│   ├── config/                 # Workout configurations
│   ├── persistence/            # SQLite database repository & data models
│   ├── state/                  # Streamlit session state management
│   ├── tracking/               # Real-time rep counting & posture metrics
│   ├── ui/                     # Custom styling & WebRTC visual themes
│   └── vision/                 # OpenCV & MediaPipe video processing stream
├── static/                     # CSS stylesheets & font assets
├── requirements.txt            # Python dependencies (pinned for stability)
└── main.py                     # Streamlit application entry point
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- A **Webcam** for real-time tracking.
- A free **Groq API Key** for AI Voice Coaching.

### 2. Clone the Repository
```bash
git clone https://github.com/Ronakjain935/AI_REAL-TIME_GYM_COACH.git
cd AI_REAL-TIME_GYM_COACH
```

### 3. Create a Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Linux/macOS)
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your Groq API Key:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GROQ_API_KEY="your_groq_api_key_here"
```

### 5. Run the Application
```bash
streamlit run main.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔧 Troubleshooting & Known Issues

- **WebRTC Camera Access**: Ensure camera access is allowed in your web browser. If the webcam stream does not initialize, check your privacy settings to grant camera access to your browser on `localhost`.
- **Starlette ASGI Middleware Compatibility**: Streamlit requires `starlette>=0.46.0,<1.0.0`. Installing Starlette 1.x causes `TypeError: GZipResponder.__init__() missing 1 required keyword-only argument`. This project's `requirements.txt` has pinned compatibility bounds to avoid this.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it!