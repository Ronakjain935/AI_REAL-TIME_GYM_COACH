#!/usr/bin/env bash
set -o errexit

apt-get update && apt-get install -y libgles2-mesa-dev libgl1-mesa-glx libegl1-mesa || true
pip install --upgrade pip
pip install -r requirements.txt
