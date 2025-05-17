import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app_name, log_dir='logs'):
    """Setup logging configuration"""
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f'{app_name}.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_network_interfaces():
    """Get available network interfaces"""
    interfaces = []
    net_dir = '/sys/class/net'
    
    if os.path.exists(net_dir):
        for iface in os.listdir(net_dir):
            if iface != 'lo':  # Skip loopback
                interfaces.append(iface)
    
    return interfaces