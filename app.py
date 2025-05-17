#!/usr/bin/env python3
import json
import os

from flask import Flask

from vm_pool.api import register_routes
from vm_pool.pool_manager import VMPoolManager
from vm_pool.utils import setup_logging

# Setup logging
logger = setup_logging('vm-rental-service')
logger.info('Starting VM Rental Service')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)
    logger.info('Configuration loaded')

with open('config/vm_templates.json', 'r') as f:
    vm_templates = json.load(f)
    logger.info('VM templates loaded')

# Create Flask app
app = Flask(__name__)

# Initialize VM Pool Manager
logger.info('Initializing VM Pool Manager')
pool_manager = VMPoolManager(config, vm_templates)

# Register API routes
register_routes(app, pool_manager)

if __name__ == '__main__':
    logger.info(f"Starting API server on {config['server']['host']}:{config['server']['port']}")
    app.run(
        host=config['server']['host'],
        port=config['server']['port']
    )