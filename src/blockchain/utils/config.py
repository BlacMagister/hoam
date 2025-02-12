import os
import yaml
from typing import Dict, Any
from pathlib import Path

class ConfigLoader:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.load_order = [
            'config/default.yml',
            'config/local.yml',
            os.getenv('BLOCKCHAIN_CONFIG', 'config/production.yml')
        ]
        
    def load(self):
        for config_path in self.load_order:
            path = Path(config_path)
            if path.exists():
                with open(path) as f:
                    self.config.update(yaml.safe_load(f))
                    
        # Override with environment variables
        self.config['network']['port'] = int(os.getenv('NETWORK_PORT', self.config['network']['port']))
        self.config['database']['path'] = os.getenv('DB_PATH', self.config['database']['path'])
        
    def get(self, key: str, default=None) -> Any:
        return self.config.get(key, default)
