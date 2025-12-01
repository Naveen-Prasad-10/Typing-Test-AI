#!/bin/bash
export FLASK_APP=app.py
export FLASK_ENV=production
gunicorn -b 0.0.0.0:${PORT:-5000} app:app
chmod +x start.sh
