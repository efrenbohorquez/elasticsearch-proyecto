"""
Módulo de indexación de documentos
Maneja la carga e indexación de documentos en Elasticsearch.
"""
from elasticsearch.helpers import bulk
from datetime import datetime
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)


class DocumentIndexer:
    """Gestor de indexación de documentos."""
    
    def __init__(self, es_client):
        """
        Inicializa el indexador de documentos.
        
        Args:
            es_client: Cliente de Elasticsearch conectado
        """
        self.es = es_client
        self.index_name = Config.INDEX_NAME
    
    def validate_document(self, document):
        """
        Valida que un documento tenga los campos requeridos.
        
        Args:
            document: Documento a validar
            
        Returns:
            bool: True si el documento es válido
            
        Raises:
            ValueError: Si faltan campos requeridos
        """
        required_fields = ['autor', 'tipo_documento', 'texto', 'fecha']
        
        for field in required_fields:
            if field not in document:
                raise ValueError(f"Falta el campo requerido: {field}")
        
        # Validar formato de fecha
        try:
            datetime.strptime(document['fecha'], '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Formato de fecha inválido: {document['fecha']}. Usa YYYY-MM-DD")
        
        return True
    
    def index_single_document(self, document, doc_id=None):
        """
        Indexa un solo documento.
        
        Args:
            document: Documento a indexar
            doc_id: ID del documento (opcional)
            
        Returns:
            dict: Respuesta de Elasticsearch
        """
        try:
            # Validar documento
            self.validate_document(document)
            
            # Indexar
            response = self.es.index(
                index=self.index_name,
                id=doc_id,
                document=document
            )
            
            logger.info(f"✓ Documento indexado: ID={response['_id']}")
            return response
            
        except Exception as e:
            logger.error(f"Error al indexar documento: {e}")
            raise
    
    def index_bulk_documents(self, documents):
        """
        Indexa múltiples documentos usando bulk API.
        
        Args:
            documents: Lista de documentos a indexar
            
        Returns:
            tuple: (éxitos, errores)
        """
        try:
            logger.info(f"Iniciando indexación masiva de {len(documents)} documentos...")
            
            # Validar todos los documentos
            for i, doc in enumerate(documents):
                self.validate_document(doc)
            
            # Preparar acciones para bulk
            actions = []
            for i, doc in enumerate(documents, start=1):
                action = {
                    "_index": self.index_name,
                    "_id": i,
                    "_source": doc
                }
                actions.append(action)
            
            # Ejecutar bulk
            success_count, errors = bulk(
                self.es,
                actions,
                stats_only=False,
                raise_on_error=False
            )
            
            logger.info(f"✓ Indexación completada:")
            logger.info(f"  - Documentos exitosos: {success_count}")
            
            if errors:
                error_count = len(errors)
                logger.warning(f"  - Errores: {error_count}")
                for error in errors[:5]:  # Mostrar solo los primeros 5 errores
                    logger.error(f"    Error: {error}")
            
            return success_count, errors
            
        except Exception as e:
            logger.error(f"Error en indexación masiva: {e}")
            raise
    
    def count_documents(self):
        """
        Cuenta los documentos en el índice.
        
        Returns:
            int: Número de documentos
        """
        try:
            result = self.es.count(index=self.index_name)
            count = result['count']
            logger.info(f"Total de documentos en '{self.index_name}': {count}")
            return count
        except Exception as e:
            logger.error(f"Error al contar documentos: {e}")
            raise
    
    def get_document_by_id(self, doc_id):
        """
        Obtiene un documento por su ID.
        
        Args:
            doc_id: ID del documento
            
        Returns:
            dict: Documento encontrado
        """
        try:
            response = self.es.get(index=self.index_name, id=doc_id)
            return response['_source']
        except Exception as e:
            logger.error(f"Error al obtener documento {doc_id}: {e}")
            raise
    
    def delete_document(self, doc_id):
        """
        Elimina un documento por su ID.
        
        Args:
            doc_id: ID del documento a eliminar
            
        Returns:
            dict: Respuesta de Elasticsearch
        """
        try:
            response = self.es.delete(index=self.index_name, id=doc_id)
            logger.info(f"✓ Documento {doc_id} eliminado")
            return response
        except Exception as e:
            logger.error(f"Error al eliminar documento {doc_id}: {e}")
            raise
