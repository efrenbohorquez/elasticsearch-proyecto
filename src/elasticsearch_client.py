"""
Módulo de conexión a Elasticsearch
Gestiona la conexión y operaciones básicas con el servidor.
"""
from typing import Optional, Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, AuthenticationException
from src.config import Config, ConfigError
from src.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)


class ElasticsearchClient:
    """Cliente para gestionar la conexión a Elasticsearch con soporte de context manager."""
    
    def __init__(self):
        """Inicializa el cliente de Elasticsearch."""
        self.client: Optional[Elasticsearch] = None
        self.is_connected: bool = False
    
    def __enter__(self):
        """Permite usar el cliente con context manager."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra automáticamente la conexión al salir del contexto."""
        self.disconnect()
        return False
        
    def connect(self) -> bool:
        """
        Establece conexión con Elasticsearch.
        
        Returns:
            bool: True si la conexión fue exitosa
            
        Raises:
            ConnectionError: Si no se puede conectar al servidor
            AuthenticationException: Si las credenciales son inválidas
            ConfigError: Si la configuración es inválida
        """
        try:
            logger.info("Intentando conectar a Elasticsearch...")
            
            # Validar configuración
            Config.validate()
            
            # Obtener URL y configuración de autenticación
            url = Config.get_elastic_url()
            auth_config = Config.get_auth_config()
            
            logger.info(f"Conectando a: {url}")
            logger.info(f"Método de autenticación: {'API Key' if 'api_key' in auth_config else 'Usuario/Contraseña'}")
            
            # Crear cliente con configuración optimizada
            self.client = Elasticsearch(
                url,
                **auth_config,
                request_timeout=Config.REQUEST_TIMEOUT,
                max_retries=Config.MAX_RETRIES,
                retry_on_timeout=True,
                verify_certs=True
            )
            
            # Verificar conexión
            if not self.client.ping():
                logger.error("✗ Fallo en la conexión: El servidor no responde")
                return False
            
            # Obtener información del servidor
            info = self.client.info()
            self.is_connected = True
            
            logger.info("✓ Conexión exitosa a Elasticsearch")
            logger.info(f"  - Versión del servidor: {info['version']['number']}")
            logger.info(f"  - Cluster: {info['cluster_name']}")
            
            return True
                
        except ConfigError as e:
            logger.error(f"✗ Error de configuración: {e}")
            raise
            
        except AuthenticationException as e:
            logger.error(f"✗ Error de autenticación: {e}")
            logger.error("Verifica que tu API_KEY o credenciales sean correctas")
            raise
            
        except ConnectionError as e:
            logger.error(f"✗ Error de conexión: {e}")
            logger.error("Verifica que el CLOUD_ID sea correcto y que tengas conexión a internet")
            raise
            
        except Exception as e:
            logger.error(f"✗ Error inesperado al conectar: {e}")
            raise
    
    
    def disconnect(self) -> None:
        """Cierra la conexión a Elasticsearch."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Conexión cerrada")
    
    def get_client(self) -> Elasticsearch:
        """
        Obtiene el cliente de Elasticsearch.
        
        Returns:
            Elasticsearch: Cliente conectado
            
        Raises:
            RuntimeError: Si no hay conexión establecida
        """
        if not self.is_connected or not self.client:
            raise RuntimeError("No hay conexión a Elasticsearch. Llama a connect() primero.")
        return self.client
    
    def check_health(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del cluster.
        
        Returns:
            dict: Información del estado del cluster
        """
        try:
            client = self.get_client()
            
            # Intentar obtener health del cluster (no disponible en serverless)
            try:
                health = client.cluster.health()
                logger.info(f"Estado del cluster: {health['status']}")
                logger.info(f"Nodos: {health['number_of_nodes']}")
                logger.info(f"Índices activos: {health['active_primary_shards']}")
                return health
            except Exception:
                # Modo serverless - usar verificación alternativa
                logger.info("Modo Serverless detectado - usando verificación alternativa")
                info = client.info()
                logger.info(f"Cluster UUID: {info.get('cluster_uuid', 'N/A')}")
                return {'status': 'serverless', 'info': info}
            
        except Exception as e:
            logger.error(f"Error al verificar salud del cluster: {e}")
            raise
