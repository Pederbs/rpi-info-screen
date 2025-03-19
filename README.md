# RPi - Info Screen
A rudamentery info screen showing wether data and bus time tables for the closest bus stop. 

## Usage

Download requirements and run `app.py`

## Automatic run of app on boot

1. Create the Service File

```
sudo nano /etc/systemd/system/rpi-info-screen.service
```

2. Add the Following:

```
[Unit]
Description=Auto-update and run Raspberry Pi Info Screen
After=network.target

[Service]
User=Familien
WorkingDirectory=/home/Familien/git/rpi-info-screen
ExecStart=/bin/bash /home/Familien/git/rpi-info-screen/auto_update.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and Start the Service

```
sudo systemctl daemon-reload
sudo systemctl enable rpi-info-screen
sudo systemctl start rpi-info-screen
```

### Auto-Open Browser in Fullscreen

1. Make `start_browser.sh` executable:

```
chmod +x /home/Familien/git/rpi-info-screen/start_browser.sh
```

2. Add It to ~/.config/lxsession/LXDE-pi/autostart

```
mkdir -p ~/.config/lxsession/LXDE-pi
nano ~/.config/lxsession/LXDE-pi/autostart
```

3. Add This Line to the File:

```
@/home/Familien/git/rpi-info-screen/start_browser.sh
```