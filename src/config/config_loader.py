# src/config/loader.py
import os
import yaml
from typing import Dict
from pathlib import Path

class ConfigurationLoader:
    _instance = None
    _config = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._config = self._load_config()

    def _load_config(self) -> Dict:
        app_name = os.getenv('APP_NAME', 'myapp')
        environment = os.getenv('ENV', 'development')

        config_path = Path(__file__).parent.parent.parent / 'config' / f'{app_name}.yml'

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found for app: {app_name}")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        env_config = config.get(environment)
        if not env_config:
            raise ValueError(f"Environment '{environment}' not found in config")

        return env_config

    def get_config(self) -> Dict:
        return self._config