"""
Módulo de indexación de documentos
Maneja la carga e indexación de documentos en Elasticsearch.
"""
from typing import Dict, Any, List, Tuple
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from datetime import datetime
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)


class DocumentIndexer:
    """Gestor de indexación de documentos."""
    
    REQUIRED_FIELDS = ['autor', 'tipo_documento', 'texto', 'fecha']
    DATE_FORMAT = '%Y-%m-%d'
    
    def __init__(self, es_client: Elasticsearch):
        """
        Inicializa el indexador de documentos.
        
        Args:
            es_client: Cliente de Elasticsearch conectado
        """
        self.es = es_client
        self.index_name = Config.INDEX_NAME
    
    def validate_document(self, document: Dict[str, Any]) -> bool:
        """
        Valida que un documento tenga los campos requeridos.
        
        Args:
            document: Documento a validar
            
        Returns:
            bool: True si el documento es válido
            
        Raises:
            ValueError: Si faltan campos requeridos o el formato es inválido
        """
        # Validar campos requeridos
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in document]
        if missing_fields:
            raise ValueError(f"Faltan campos requeridos: {', '.join(missing_fields)}")
        
        # Validar formato de fecha
        try:
            datetime.strptime(document['fecha'], self.DATE_FORMAT)
        except ValueError:
            raise ValueError(
                f"Formato de fecha inválido: {document['fecha']}. "
                f"Usa formato {self.DATE_FORMAT}"
            )
        
        return True
    
    def index_single_document(self, document: Dict[str, Any], doc_id: Any = None) -> Dict[str, Any]:
        """
        Indexa un solo documento.
        
        Args:
            document: Documento a indexar
            doc_id: ID del documento (opcional)
            
        Returns:
            dict: Respuesta de Elasticsearch
        """
        try:
            self.validate_document(document)
            
            response = self.es.index(
                index=self.index_name,
                id=doc_id,
                document=document
            )
            
            logger.info("✓ Documento indexado: ID=%s", response['_id'])
            return response
            
        except Exception as e:
            logger.error("Error al indexar documento: %s", e)
            raise
    
    def index_bulk_documents(self, documents: List[Dict[str, Any]]) -> Tuple[int, List]:
        """
        Indexa múltiples documentos usando bulk API para mayor eficiencia.
        
        Args:
            documents: Lista de documentos a indexar
            
        Returns:
            tuple: (éxitos, errores)
        """
        try:
            logger.info("Iniciando indexación masiva de %d documentos...", len(documents))
            
            # Validar todos los documentos primero
            for i, doc in enumerate(documents, 1):
                try:
                    self.validate_document(doc)
                except ValueError as e:
                    logger.error("Error de validación en documento %d: %s", i, e)
                    raise
            
            # Preparar acciones para bulk
            actions = [
                {
                    "_index": self.index_name,
                    "_id": i,
                    "_source": doc
                }
                for i, doc in enumerate(documents, start=1)
            ]
            
            # Ejecutar bulk
            success_count, errors = bulk(
                self.es,
                actions,
                stats_only=False,
                raise_on_error=False
            )
            
            logger.info("✓ Indexación completada:")
            logger.info("  - Documentos exitosos: %d", success_count)
            
            if errors:
                logger.warning("  - Errores: %d", len(errors))
                for error in errors[:5]:  # Mostrar solo los primeros 5 errores
                    logger.error("    Error: %s", error)
            
            return success_count, errors
            
        except Exception as e:
            logger.error("Error en indexación masiva: %s", e)
            raise
    
    def count_documents(self) -> int:
        """
        Cuenta los documentos en el índice.
        
        Returns:
            int: Número de documentos
        """
        try:
            result = self.es.count(index=self.index_name)
            count = result['count']
            logger.info("Total de documentos en '%s': %d", self.index_name, count)
            return count
        except Exception as e:
            logger.error("Error al contar documentos: %s", e)
            raise
    
    def get_document_by_id(self, doc_id: Any) -> Dict[str, Any]:
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
            logger.error("Error al obtener documento %s: %s", doc_id, e)
            raise
    
    def delete_document(self, doc_id: Any) -> Dict[str, Any]:
        """
        Elimina un documento por su ID.
        
        Args:
            doc_id: ID del documento a eliminar
            
        Returns:
            dict: Respuesta de Elasticsearch
        """
        try:
            response = self.es.delete(index=self.index_name, id=doc_id)
            logger.info("✓ Documento %s eliminado", doc_id)
            return response
        except Exception as e:
            logger.error("Error al eliminar documento %s: %s", doc_id, e)
            raise
