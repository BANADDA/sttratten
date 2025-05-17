# VM Rental Service

A server-based VM rental service with warm pooling for instant VM assignment.

## Overview

This service manages pools of pre-created VMs for instant assignment. Users receive simple connection details (IP, username, port) and can connect directly to the VM without handling any keys or authentication.

## Features

- Pre-created warm VM pools for instant assignment
- Support for Ubuntu and Windows VMs
- Simple API for VM request and release
- Connection persistence for reliable remote access
- Server-side key management (no key handling for users)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/BANADDA/vm-rental-service
   cd vm-rental-service
   ```

2. Run the setup script:
   ```
   bash scripts/setup.sh
   ```

3. Configure the service:
   - Edit `config/config.json` with your settings
   - Edit `config/vm_templates.json` with your VM template paths

4. Create VM templates:
   ```
   bash scripts/create_vm_template.sh ubuntu /path/to/ubuntu.iso
   bash scripts/create_vm_template.sh windows /path/to/windows.iso
   ```

5. Generate SSH keys:
   ```
   ssh-keygen -t rsa -b 4096 -f config/ssh_config/server_key
   ```

6. Install as a service (optional):
   ```
   bash scripts/service_install.sh
   ```

## Usage

### Request a VM

```
curl -X POST http://localhost:5000/api/vms/request -H "Content-Type: application/json" -d '{"type": "ubuntu"}'
```

### Release a VM

```
curl -X POST http://localhost:5000/api/vms/release/<vm_id>
```

### Check Available VMs

```
curl http://localhost:5000/api/vms/available
```

## Architecture

- **VM Pool Manager**: Maintains pools of pre-created VMs
- **API Service**: Provides endpoints for VM management
- **Warm VM Pools**: Pre-created VMs ready for instant assignment
- **Server Private Key**: Used internally for VM management
