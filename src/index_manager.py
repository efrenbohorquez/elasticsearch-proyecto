"""
Módulo de gestión de índices
Maneja la creación, configuración y eliminación de índices en Elasticsearch.
"""
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)


class IndexManager:
    """Gestor de índices de Elasticsearch."""
    
    def __init__(self, es_client):
        """
        Inicializa el gestor de índices.
        
        Args:
            es_client: Cliente de Elasticsearch conectado
        """
        self.es = es_client
        self.index_name = Config.INDEX_NAME
    
    def get_mapping_configuration(self):
        """
        Obtiene la configuración del mapping para el índice de cuentos.
        
        Returns:
            dict: Configuración completa del mapping
        """
        return {
            "settings": {
                # En modo serverless, no se pueden configurar shards y replicas
                "analysis": {
                    "analyzer": {
                        "spanish_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "asciifolding",
                                "spanish_stop",
                                "spanish_stemmer"
                            ]
                        }
                    },
                    "filter": {
                        "spanish_stop": {
                            "type": "stop",
                            "stopwords": "_spanish_"
                        },
                        "spanish_stemmer": {
                            "type": "stemmer",
                            "language": "spanish"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "autor": {
                        "type": "keyword"
                    },
                    "tipo_documento": {
                        "type": "keyword"
                    },
                    "fecha": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "texto": {
                        "type": "text",
                        "analyzer": "spanish_analyzer",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            }
        }
    
    def index_exists(self):
        """
        Verifica si el índice existe.
        
        Returns:
            bool: True si el índice existe
        """
        try:
            exists = self.es.indices.exists(index=self.index_name)
            return exists
        except Exception as e:
            logger.error(f"Error al verificar existencia del índice: {e}")
            raise
    
    def delete_index(self):
        """
        Elimina el índice si existe.
        
        Returns:
            bool: True si se eliminó o no existía
        """
        try:
            if self.index_exists():
                self.es.indices.delete(index=self.index_name)
                logger.info(f"✓ Índice '{self.index_name}' eliminado exitosamente")
                return True
            else:
                logger.info(f"El índice '{self.index_name}' no existe")
                return True
        except Exception as e:
            logger.error(f"Error al eliminar el índice: {e}")
            raise
    
    def create_index(self, delete_if_exists=False):
        """
        Crea el índice con la configuración especificada.
        
        Args:
            delete_if_exists: Si es True, elimina el índice existente antes de crear
            
        Returns:
            bool: True si se creó exitosamente
        """
        try:
            # Eliminar índice si existe y se solicita
            if delete_if_exists and self.index_exists():
                self.delete_index()
            
            # Verificar si ya existe
            if self.index_exists():
                logger.warning(f"El índice '{self.index_name}' ya existe")
                return False
            
            # Obtener configuración del mapping
            mapping_config = self.get_mapping_configuration()
            
            # Crear índice
            self.es.indices.create(
                index=self.index_name,
                body=mapping_config
            )
            
            logger.info(f"✓ Índice '{self.index_name}' creado exitosamente")
            logger.info(f"  - Analizador: spanish_analyzer")
            logger.info(f"  - Campos: autor, tipo_documento, fecha, texto")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al crear el índice: {e}")
            raise
    
    def get_index_info(self):
        """
        Obtiene información del índice.
        
        Returns:
            dict: Información del índice
        """
        try:
            if not self.index_exists():
                logger.warning(f"El índice '{self.index_name}' no existe")
                return None
            
            # Obtener información del índice
            info = self.es.indices.get(index=self.index_name)
            
            # En modo serverless, stats no está disponible
            # Usar count en su lugar
            try:
                stats = self.es.indices.stats(index=self.index_name)
                doc_count = stats['_all']['primaries']['docs']['count']
                size = stats['_all']['primaries']['store']['size_in_bytes']
            except Exception:
                # Modo serverless - usar count alternativo
                count_result = self.es.count(index=self.index_name)
                doc_count = count_result['count']
                size = 0  # No disponible en serverless
                logger.info("Modo Serverless - estadísticas de tamaño no disponibles")
            
            logger.info(f"Información del índice '{self.index_name}':")
            logger.info(f"  - Documentos: {doc_count}")
            if size > 0:
                logger.info(f"  - Tamaño: {size / 1024:.2f} KB")
            
            return {
                'index_info': info,
                'doc_count': doc_count,
                'size_bytes': size
            }
            
        except Exception as e:
            logger.error(f"Error al obtener información del índice: {e}")
            raise
    
    def refresh_index(self):
        """
        Refresca el índice para que los cambios sean visibles inmediatamente.
        """
        try:
            self.es.indices.refresh(index=self.index_name)
            logger.debug(f"Índice '{self.index_name}' refrescado")
        except Exception as e:
            logger.error(f"Error al refrescar el índice: {e}")
            raise
