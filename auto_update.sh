#!/bin/bash

# Paths
PROJECT_DIR="/home/peder/git/rpi-info-screen"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON="$VENV_DIR/bin/python"

# Interval for checking updates (in seconds)
INTERVAL=300  # Every 5 minutes

cd "$PROJECT_DIR" || exit

while true; do
    # Fetch latest changes from main
    git fetch origin main

    # Check if there are new changes
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/main)

    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        echo "New updates detected, restarting app..."
        
        # Kill existing process (modify if running differently)
        pkill -f "app.py"

        # Pull latest changes
        git pull origin main

        # Install dependencies if requirements.txt changed
        if git diff --name-only HEAD@{1} HEAD | grep -q "requirements.txt"; then
            echo "New dependencies detected, installing..."
            $VENV_DIR/bin/pip install -r requirements.txt
        fi

        # Restart the application
        echo "Restarting app..."
        nohup $PYTHON app.py > app.log 2>&1 &

        # Wait a few seconds to ensure the app starts
        sleep 5

        # Restart Chromium in fullscreen mode
        nohup chromium-browser --kiosk --disable-session-crashed-bubble --disable-infobars http://localhost:5000 > browser.log 2>&1 &
    fi

    # Sleep for the defined interval before checking again
    sleep $INTERVAL
done
