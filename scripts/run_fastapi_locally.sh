#!/bin/bash

# Function to terminate both processes
cleanup() {
    echo "Terminating processes..."
    # Check if the processes are still running before attempting to kill them
    if ps -p $uvicorn_pid > /dev/null 2>&1; then
        kill $uvicorn_pid
    fi
    if ps -p $gunicorn_pid > /dev/null 2>&1; then
        kill $gunicorn_pid
    fi
    wait
}

# Trap Ctrl+C (SIGINT) and call the cleanup function
trap 'cleanup; trap - SIGINT; kill -SIGINT $$' SIGINT

# Start uvicorn in the background and save its PID
uvicorn prompt_leakage_probing.deployment.main_1_fastapi:app --port 8008 --reload &
uvicorn_pid=$!

# Start gunicorn in the background and save its PID
gunicorn prompt_leakage_probing.deployment.main_2_mesop:app -b 0.0.0.0:8888 --reload &
gunicorn_pid=$!

# Wait for both processes to finish
wait
