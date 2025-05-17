import subprocess
import time
import uuid

import libvirt


def create_vm(conn, vm_type, template_config):
    """Create a new VM of specified type with pre-installed key"""
    vm_id = str(uuid.uuid4())
    vm_name = f"{vm_type}-{vm_id[:8]}"
    
    # Clone the base image for this VM
    disk_path = f"/var/lib/libvirt/images/{vm_name}.qcow2"
    subprocess.run([
        "qemu-img", "create", 
        "-f", "qcow2", 
        "-b", template_config["base_image"], 
        disk_path
    ])
    
    # Setup network configuration for persistent connections
    net_config = f"""
    <interface type='network'>
      <source network='default'/>
      <model type='{template_config['network_config']['model']}'/>
      <driver name='vhost' queues='{template_config['network_config']['queues']}'/>
      <tune>
        <sndbuf>262144</sndbuf>
      </tune>
    </interface>
    """
    
    # Define VM XML configuration
    xml_desc = f"""
    <domain type='kvm'>
      <name>{vm_name}</name>
      <memory unit='MB'>{template_config['memory']}</memory>
      <vcpu placement='static'>{template_config['vcpus']}</vcpu>
      <cpu mode='host-passthrough'/>
      <os>
        <type arch='x86_64'>hvm</type>
        <boot dev='hd'/>
      </os>
      <features>
        <acpi/>
        <apic/>
      </features>
      <devices>
        <disk type='file' device='disk'>
          <driver name='qemu' type='qcow2' cache='none' io='native'/>
          <source file='{disk_path}'/>
          <target dev='vda' bus='virtio'/>
        </disk>
        {net_config}
        <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
          <listen type='address' address='0.0.0.0'/>
        </graphics>
        <video>
          <model type='virtio'/>
        </video>
      </devices>
    </domain>
    """
    
    # Create and start the VM
    domain = conn.defineXML(xml_desc)
    domain.create()
    
    # Wait for VM to boot and get IP
    ip_address = wait_for_ip(domain)
    
    # Create VM record
    vm_record = {
        "id": vm_id,
        "name": vm_name,
        "type": vm_type,
        "domain": domain,
        "ip_address": ip_address,
        "status": "available",
        "created_at": time.time()
    }
    
    return vm_record

def wait_for_ip(domain, timeout=120):
    """Wait for the VM to get an IP address"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
            for iface in ifaces.values():
                for addr in iface["addrs"]:
                    if addr["type"] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                        return addr["addr"]
        except:
            pass
        time.sleep(1)
    raise Exception("Timed out waiting for VM IP address")

def reset_vm(vm):
    """Reset a VM to clean state"""
    try:
        if vm["type"] == "ubuntu":
            # For Linux VMs, we can use a management network or agent
            # that doesn't require authentication
            domain = vm["domain"]
            # Simply reboot for a clean slate if VMs use non-persistent storage
            domain.reboot()
        else:  # Windows
            # For Windows, simply reboot
            vm["domain"].reboot()
            
    except Exception as e:
        print(f"Error resetting VM {vm['id']}: {e}")
        # Fall back to reboot if reset fails
        try:
            vm["domain"].reboot()
        except:
            pass