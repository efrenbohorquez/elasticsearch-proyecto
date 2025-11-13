"""
Módulo de conexión a Elasticsearch
Gestiona la conexión y operaciones básicas con el servidor.
"""
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, AuthenticationException
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)


class ElasticsearchClient:
    """Cliente para gestionar la conexión a Elasticsearch."""
    
    def __init__(self):
        """Inicializa el cliente de Elasticsearch."""
        self.client = None
        self.is_connected = False
        
    def connect(self):
        """
        Establece conexión con Elasticsearch.
        
        Returns:
            bool: True si la conexión fue exitosa
            
        Raises:
            ConnectionError: Si no se puede conectar al servidor
            AuthenticationException: Si las credenciales son inválidas
        """
        try:
            logger.info("Intentando conectar a Elasticsearch...")
            
            # Validar configuración
            Config.validate()
            
            # Crear cliente
            # Usar URL directa con https
            url = Config.ELASTIC_CLOUD_ID
            if not url.startswith('http'):
                url = f"https://{url}"
            
            logger.info(f"Conectando a: {url}")
            
            # Determinar método de autenticación
            if Config.ELASTIC_API_KEY:
                logger.info("Usando autenticación con API Key")
                self.client = Elasticsearch(
                    url,
                    api_key=Config.ELASTIC_API_KEY,
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True,
                    verify_certs=True
                )
            elif Config.ELASTIC_PASSWORD:
                logger.info(f"Usando autenticación con usuario: {Config.ELASTIC_USER}")
                self.client = Elasticsearch(
                    url,
                    basic_auth=(Config.ELASTIC_USER, Config.ELASTIC_PASSWORD),
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True,
                    verify_certs=True
                )
            else:
                raise ValueError("Se requiere ELASTIC_API_KEY o ELASTIC_PASSWORD en .env")
            
            # Verificar conexión
            if self.client.ping():
                info = self.client.info()
                version = info['version']['number']
                cluster_name = info['cluster_name']
                
                self.is_connected = True
                logger.info(f"✓ Conexión exitosa a Elasticsearch")
                logger.info(f"  - Versión del servidor: {version}")
                logger.info(f"  - Cluster: {cluster_name}")
                
                return True
            else:
                logger.error("✗ Fallo en la conexión: El servidor no responde")
                return False
                
        except AuthenticationException as e:
            logger.error(f"✗ Error de autenticación: {e}")
            logger.error("Verifica que tu API_KEY sea correcta")
            raise
            
        except ConnectionError as e:
            logger.error(f"✗ Error de conexión: {e}")
            logger.error("Verifica que el CLOUD_ID sea correcto y que tengas conexión a internet")
            raise
            
        except Exception as e:
            logger.error(f"✗ Error inesperado al conectar: {e}")
            raise
    
    def disconnect(self):
        """Cierra la conexión a Elasticsearch."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Conexión cerrada")
    
    def get_client(self):
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
    
    def check_health(self):
        """
        Verifica el estado de salud del cluster.
        
        Returns:
            dict: Información del estado del cluster
        """
        try:
            client = self.get_client()
            
            # En modo serverless, cluster.health no está disponible
            # Usamos info() en su lugar
            try:
                health = client.cluster.health()
                logger.info(f"Estado del cluster: {health['status']}")
                logger.info(f"Nodos: {health['number_of_nodes']}")
                logger.info(f"Índices: {health['active_primary_shards']}")
                return health
            except Exception:
                # Modo serverless - usar info alternativo
                logger.info("Modo Serverless detectado - usando verificación alternativa")
                info = client.info()
                logger.info(f"Cluster UUID: {info.get('cluster_uuid', 'N/A')}")
                return {'status': 'serverless', 'info': info}
            
        except Exception as e:
            logger.error(f"Error al verificar salud del cluster: {e}")
            raise
