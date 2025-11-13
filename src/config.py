"""
Módulo de configuración
Carga las variables de entorno y configuración del sistema.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Config:
    """Clase de configuración centralizada."""
    
    # Elasticsearch
    ELASTIC_CLOUD_ID = os.getenv('ELASTIC_CLOUD_ID', '')
    ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY', '')
    ELASTIC_USER = os.getenv('ELASTIC_USER', 'elastic')
    ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', '')
    INDEX_NAME = os.getenv('INDEX_NAME', 'index_cuentos')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/elasticsearch.log'
    
    # Validación
    @classmethod
    def validate(cls):
        """Valida que las configuraciones necesarias estén presentes."""
        if not cls.ELASTIC_CLOUD_ID:
            raise ValueError("ELASTIC_CLOUD_ID no está configurado en .env")
        if not cls.ELASTIC_API_KEY and not cls.ELASTIC_PASSWORD:
            raise ValueError("Se requiere ELASTIC_API_KEY o ELASTIC_PASSWORD en .env")
        return True
