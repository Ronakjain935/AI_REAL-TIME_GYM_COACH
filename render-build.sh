#!/usr/bin/env bash
# Render Native Build Script
set -o errexit

echo "==> Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

echo "==> Installing Python production dependencies..."
pip install -r requirements.txt

echo "==> Render Build Completed Successfully."
