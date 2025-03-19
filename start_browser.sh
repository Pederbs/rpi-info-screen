#!/bin/bash
sleep 10  # Wait for the server to start
chromium-browser --kiosk --disable-session-crashed-bubble --disable-infobars http://localhost:5000
