"""
Módulo de configuración
Carga las variables de entorno y configuración del sistema.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""
    ...


class Config:
    """Clase de configuración centralizada con validación y caché."""
    
    _validated: bool = False
    
    # Elasticsearch
    ELASTIC_CLOUD_ID: str = os.getenv('ELASTIC_CLOUD_ID', '')
    ELASTIC_API_KEY: str = os.getenv('ELASTIC_API_KEY', '')
    ELASTIC_USER: str = os.getenv('ELASTIC_USER', 'elastic')
    ELASTIC_PASSWORD: str = os.getenv('ELASTIC_PASSWORD', '')
    INDEX_NAME: str = os.getenv('INDEX_NAME', 'index_cuentos')
    
    # Configuración de conexión
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = 'logs/elasticsearch.log'
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_elastic_url(cls) -> str:
        """Obtiene la URL de Elasticsearch con formato correcto (con caché)."""
        url = cls.ELASTIC_CLOUD_ID
        if not url.startswith('http'):
            url = f"https://{url}"
        return url
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que las configuraciones necesarias estén presentes."""
        if cls._validated:
            return True
            
        errors = []
        
        if not cls.ELASTIC_CLOUD_ID:
            errors.append("ELASTIC_CLOUD_ID no está configurado en .env")
        
        if not cls.ELASTIC_API_KEY and not cls.ELASTIC_PASSWORD:
            errors.append("Se requiere ELASTIC_API_KEY o ELASTIC_PASSWORD en .env")
        
        if cls.REQUEST_TIMEOUT <= 0:
            errors.append("REQUEST_TIMEOUT debe ser mayor a 0")
        
        if cls.MAX_RETRIES < 0:
            errors.append("MAX_RETRIES debe ser mayor o igual a 0")
        
        if errors:
            raise ConfigError("; ".join(errors))
        
        cls._validated = True
        return True
    
    @classmethod
    def get_auth_config(cls) -> dict:
        """Obtiene la configuración de autenticación apropiada."""
        if cls.ELASTIC_API_KEY:
            return {'api_key': cls.ELASTIC_API_KEY}
        return {'basic_auth': (cls.ELASTIC_USER, cls.ELASTIC_PASSWORD)}
