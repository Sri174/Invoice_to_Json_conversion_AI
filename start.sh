#!/bin/bash

# 1. Start the FastAPI backend in the background
# We run it on localhost (127.0.0.1) on port 8001 inside the Render container
echo "Starting FastAPI backend..."
uvicorn app.main:app --host 127.0.0.1 --port 8001 &

# 2. Tell Streamlit to route traffic to the internal FastAPI backend
export API_URL="http://127.0.0.1:8001/process"

# 3. Start Streamlit on the public port provided by Render
# Render assigns a random port and injects it into the $PORT variable
echo "Starting Streamlit frontend..."
streamlit run ui.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
