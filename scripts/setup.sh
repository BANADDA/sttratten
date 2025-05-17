#!/bin/bash
# Setup script for VM Rental Service

# Install required packages
echo "Installing required packages..."
sudo apt-get update
sudo apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
sudo apt-get install -y python3-libvirt python3-flask python3-pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Verify KVM installation
echo "Verifying KVM installation..."
kvm-ok

echo "Setup complete!"