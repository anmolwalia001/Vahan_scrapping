import os
from dotenv import load_dotenv
import yaml
import logging.config

# Always point to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# load_dotenv(".env")

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME"),
}

# Proxy Configuration
PROXY_CONFIG = {
    "api_key": os.getenv("PROXY_API_KEY"),
    "rotate_interval": int(os.getenv("PROXY_ROTATE_INTERVAL", 10)),  # minutes
}

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def load_logging_config():
    """Load logging.yaml config"""
    config_path = os.path.join(BASE_DIR, "configs", "logging.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

            # Fix: make sure logs directory exists
            log_dir = os.path.join(BASE_DIR, "logs")
            os.makedirs(log_dir, exist_ok=True)

            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level="INFO")