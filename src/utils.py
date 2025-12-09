"""Utility functions for the price scraper"""

import logging
import os
from pathlib import Path
from typing import Any, Dict
import yaml


def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    Path(log_dir).mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/scraper.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def get_env_variable(var_name: str, default: str = None) -> str:
    """Get environment variable with optional default"""
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set")
    return value
