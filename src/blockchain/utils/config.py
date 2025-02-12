import os
import yaml
from typing import Dict, Any
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ConfigLoader:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.load_order = [
            'config/default.yml',
            'config/local.yml',
            os.getenv('BLOCKCHAIN_CONFIG', 'config/production.yml')
        ]
        
    def load(self):
        try:
            for config_path in self.load_order:
                path = Path(config_path)
                if path.exists():
                    with open(path) as f:
                        loaded_config = yaml.safe_load(f)
                        self.config.update(loaded_config)
                        logger.info(f"Konfigurasi berhasil dimuat dari {config_path}")
                else:
                    logger.warning(f"File konfigurasi tidak ditemukan: {config_path}")
            
            # Override dengan environment variables
            self.config['network']['port'] = int(os.getenv('NETWORK_PORT', self.config['network']['port']))
            self.config['database']['path'] = os.getenv('DB_PATH', self.config['database']['path'])
            logger.info("Konfigurasi berhasil di-update dengan environment variables")
        except Exception as e:
            logger.error(f"Error saat memuat konfigurasi: {e}")
            raise

    def get(self, key: str, default=None) -> Any:
        try:
            value = self.config.get(key, default)
            logger.info(f"Mengambil konfigurasi untuk key: {key}, nilai: {value}")
            return value
        except Exception as e:
            logger.error(f"Error saat mengambil konfigurasi: {e}")
            return default
