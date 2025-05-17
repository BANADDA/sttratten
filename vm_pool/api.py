from flask import jsonify, request


def register_routes(app, pool_manager):
    """Register API routes with the Flask app"""
    
    @app.route('/')
    def index():
        return jsonify({
            "service": "VM Pool Manager",
            "version": "1.0",
            "endpoints": [
                "/api/vms/available", 
                "/api/vms/request",
                "/api/vms/release/<vm_id>",
                "/api/vms/status"
            ]
        })
    
    @app.route('/api/vms/available', methods=['GET'])
    def available_vms():
        """Get counts of available VMs by type"""
        available = pool_manager.get_available_counts()
        return jsonify(available)
    
    @app.route('/api/vms/request', methods=['POST'])
    def request_vm():
        """Request a VM assignment"""
        data = request.json
        vm_type = data.get('type')
        
        if not vm_type:
            return jsonify({"error": "Missing VM type"}), 400
        
        vm = pool_manager.assign_vm(vm_type)
        if not vm:
            return jsonify({"error": "No VMs available"}), 503
        
        return jsonify(vm)
    
    @app.route('/api/vms/release/<vm_id>', methods=['POST'])
    def release_vm(vm_id):
        """Release a VM back to the pool"""
        success = pool_manager.release_vm(vm_id)
        if not success:
            return jsonify({"error": "VM not found or already released"}), 404
        
        return jsonify({"status": "released"})
    
    @app.route('/api/vms/status', methods=['GET'])
    def system_status():
        """Get system status"""
        status = pool_manager.get_system_status()
        return jsonify(status)