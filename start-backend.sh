#!/bin/bash
# Start the backend server

cd "$(dirname "$0")"
source venv/Scripts/activate
cd Backend
python -m uvicorn main:app --reload --port 8000
