#!/bin/bash
# Script to create a VM template

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <vm_type> <base_image_path>"
    echo "Example: $0 ubuntu /path/to/ubuntu.iso"
    exit 1
fi

VM_TYPE=$1
BASE_IMAGE=$2

echo "Creating $VM_TYPE template from $BASE_IMAGE..."

# Create VM disk
qemu-img create -f qcow2 /path/to/${VM_TYPE}_template.qcow2 20G

# TODO: Add commands to set up the VM with virt-install
# This is simplified - you'd want to customize based on your needs

echo "VM template creation started. Follow the installation prompts."
echo "After installation, configure SSH/RDP and add the public key."