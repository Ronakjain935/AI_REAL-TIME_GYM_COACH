import os
import sys
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Apna AI Gym Coach - Vercel Deployment Notice</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #0F172A;
                    color: #F8FAFC;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    background: #1E293B;
                    border: 1px solid rgba(0, 242, 254, 0.3);
                    border-radius: 16px;
                    padding: 40px;
                    max-width: 640px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
                    text-align: center;
                }
                .icon {
                    font-size: 3.5rem;
                    margin-bottom: 1rem;
                }
                h1 {
                    color: #00F2FE;
                    margin-bottom: 1rem;
                    font-size: 1.8rem;
                }
                p {
                    color: #94A3B8;
                    line-height: 1.6;
                    font-size: 1rem;
                }
                .badge {
                    display: inline-block;
                    background: rgba(0, 242, 254, 0.1);
                    color: #00F2FE;
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    margin-bottom: 1.5rem;
                    border: 1px solid rgba(0, 242, 254, 0.3);
                }
                .btn {
                    display: inline-block;
                    background: linear-gradient(135deg, #00F2FE 0%, #3B82F6 100%);
                    color: #FFFFFF;
                    text-decoration: none;
                    font-weight: bold;
                    padding: 14px 28px;
                    border-radius: 8px;
                    margin-top: 1.5rem;
                    box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
                    transition: transform 0.2s ease;
                }
                .btn:hover {
                    transform: translateY(-2px);
                }
                .note {
                    margin-top: 1.5rem;
                    font-size: 0.85rem;
                    color: #64748B;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🏋️‍♂️</div>
                <div class="badge">APNA AI GYM COACH v1.0</div>
                <h1>AI Real-Time Gym Coach</h1>
                <p>
                    Real-time Computer Vision (MediaPipe + WebRTC) requires a persistent backend server with continuous streaming capabilities and C++ OpenGL drivers.
                </p>
                <p>
                    For 100% full live webcam pose detection and AI voice coaching, access the live cloud service:
                </p>
                <a href="https://ai-real-time-gym-coach-eu0b.onrender.com/" class="btn" target="_blank">Launch Live AI Camera App 🚀</a>
                <div class="note">
                    Engineered with Streamlit, Streamlit-WebRTC, MediaPipe Pose Landmarker, and OpenCV.
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))
        return
