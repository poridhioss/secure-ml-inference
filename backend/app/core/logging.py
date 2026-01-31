import logging
import sys
from app.core.config import settings

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(instance_id)s] - %(message)s"


class InstanceFilter(logging.Filter):
    """Add instance ID to log records"""
    
    def filter(self, record):
        record.instance_id = settings.INSTANCE_ID
        return True


def setup_logging():
    """Configure application logging"""
    
    # Create logger
    logger = logging.getLogger("fastapi_app")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add instance filter
    console_handler.addFilter(InstanceFilter())
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


# Create logger instance
logger = setup_logging()