#!/bin/bash

# Function to terminate both processes
cleanup() {
    echo "Terminating processes..."
    kill $uvicorn_pid $gunicorn_pid
    wait
}

# Trap Ctrl+C (SIGINT) and call the cleanup function
trap cleanup SIGINT

# Start uvicorn in the background and save its PID
uvicorn context_leakage_team.deployment.main_1_fastapi:app --port 8008 --reload &
uvicorn_pid=$!

# Start gunicorn in the background and save its PID
gunicorn context_leakage_team.deployment.main_2_mesop:app -b 0.0.0.0:8888 --reload &
gunicorn_pid=$!

# Wait for both processes to finish
wait
