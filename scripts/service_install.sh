#!/bin/bash
# Install VM Rental Service as a systemd service

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

# Create service file
cat > /tmp/vm-rental-service.service << EOF
[Unit]
Description=VM Rental Service
After=network.target

[Service]
User=root
WorkingDirectory=${PROJECT_DIR}
ExecStart=/usr/bin/python3 ${PROJECT_DIR}/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install service
sudo mv /tmp/vm-rental-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vm-rental-service.service
sudo systemctl start vm-rental-service.service

echo "Service installed and started!"
