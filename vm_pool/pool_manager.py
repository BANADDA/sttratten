import threading
import time
import uuid

import libvirt

from vm_pool.vm_operations import create_vm, reset_vm, wait_for_ip


class VMPoolManager:
    def __init__(self, config, vm_templates):
        self.config = config
        self.vm_templates = vm_templates
        self.vm_pools = {}  # Dictionary of VM pools by type
        self.assigned_vms = {}  # Tracking assigned VMs
        
        # Load server key
        self.server_key_path = config['keys']['private_key_path']
        
        # Connect to hypervisor
        self.conn = libvirt.open(config['hypervisor']['connection_uri'])
        
        # Initialize pools for each VM type
        for vm_type in vm_templates:
            self.vm_pools[vm_type] = []
        
        # Start pool maintenance thread
        self.maintenance_thread = threading.Thread(target=self.maintain_pools)
        self.maintenance_thread.daemon = True
        self.maintenance_thread.start()
    
    def maintain_pools(self):
        """Background thread to maintain VM pools at target size"""
        while True:
            for vm_type, target_size in self.config['pool']['sizes'].items():
                current_pool_size = len(self.vm_pools[vm_type])
                
                # Create VMs if pool is under target size
                if current_pool_size < target_size:
                    print(f"Pool {vm_type} under target size, creating {target_size - current_pool_size} VMs")
                    for _ in range(target_size - current_pool_size):
                        try:
                            vm = create_vm(self.conn, vm_type, self.vm_templates[vm_type])
                            self.vm_pools[vm_type].append(vm)
                            print(f"Created VM {vm['name']} with IP {vm['ip_address']}")
                        except Exception as e:
                            print(f"Error creating VM: {e}")
            
            # Run maintenance every interval seconds
            time.sleep(self.config['pool']['maintenance_interval'])
    
    def assign_vm(self, vm_type):
        """Assign a VM from the pool to a user"""
        if vm_type not in self.vm_pools or not self.vm_pools[vm_type]:
            # No VMs available in pool
            return None
        
        # Get VM from pool
        vm = self.vm_pools[vm_type].pop(0)
        
        # Update VM status
        vm["status"] = "assigned"
        vm["assigned_at"] = time.time()
        
        # Track assignment
        self.assigned_vms[vm["id"]] = vm
        
        # Generate access information
        access_info = self.generate_access_info(vm)
        
        # Return VM info with access details
        return {
            "vm_id": vm["id"],
            "name": vm["name"],
            "type": vm["type"],
            "ip_address": vm["ip_address"],
            "access": access_info
        }
    
    def generate_access_info(self, vm):
        """Generate access information - user never sees the server key"""
        # For end users, we only provide direct connection details
        return {
            "ssh": {
                "host": vm["ip_address"],
                "port": 22,
                "username": "user",
            },
            "remote_desktop": {
                "type": "vnc" if vm["type"] != "windows" else "rdp",
                "host": vm["ip_address"],
                "port": 5900 if vm["type"] != "windows" else 3389,
                "username": "user"
            }
        }
    
    def release_vm(self, vm_id):
        """Release a VM back to the pool or recycle it"""
        if vm_id not in self.assigned_vms:
            return False
        
        vm = self.assigned_vms.pop(vm_id)
        vm_type = vm["type"]
        
        # Reset the VM
        reset_vm(vm)
        
        # Return to pool
        vm["status"] = "available"
        vm["assigned_at"] = None
        self.vm_pools[vm_type].append(vm)
        
        return True
    
    def get_available_counts(self):
        """Get counts of available VMs by type"""
        available = {}
        for vm_type in self.vm_templates:
            available[vm_type] = len(self.vm_pools[vm_type])
        return available
    
    def get_system_status(self):
        """Get system status"""
        status = {
            "pools": {},
            "assigned": len(self.assigned_vms)
        }
        
        for vm_type in self.vm_templates:
            status["pools"][vm_type] = {
                "available": len(self.vm_pools[vm_type]),
                "target": self.config['pool']['sizes'][vm_type]
            }
        
        return status