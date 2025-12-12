#!/bin/bash
# Start the Flask server for the Disk Space Checker extension

cd "$(dirname "$0")"
source venv/bin/activate
python3 local_app.py

