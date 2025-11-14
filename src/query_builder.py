"""
Módulo de consultas a Elasticsearch
Implementa diferentes tipos de búsquedas usando Query DSL.
"""
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)


class QueryBuilder:
    """Constructor de consultas para Elasticsearch."""
    
    def __init__(self, es_client: Elasticsearch):
        """
        Inicializa el constructor de consultas.
        
        Args:
            es_client: Cliente de Elasticsearch conectado
        """
        self.es = es_client
        self.index_name = Config.INDEX_NAME
    
    def _execute_query(self, query: Dict[str, Any], query_name: str, include_score: bool = False) -> List[Dict[str, Any]]:
        """
        Método base para ejecutar cualquier consulta (elimina duplicación de código).
        
        Args:
            query: Consulta de Elasticsearch
            query_name: Nombre de la consulta para logging
            include_score: Si incluir el score de relevancia
            
        Returns:
            list: Lista de documentos encontrados
        """
        try:
            logger.info("Ejecutando %s...", query_name)
            response = self.es.search(index=self.index_name, body=query)
            
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            logger.info("✓ Encontrados %d documentos", total)
            
            return self._format_results(hits, include_score)
            
        except Exception as e:
            logger.error("Error en %s: %s", query_name, e)
            raise
    
    def match_all(self, size: int = 100) -> List[Dict[str, Any]]:
        """
        Consulta que devuelve todos los documentos.
        
        Args:
            size: Número máximo de documentos a devolver
            
        Returns:
            list: Lista de documentos encontrados
        """
        query = {
            "query": {"match_all": {}},
            "size": size
        }
        return self._execute_query(query, f"Match All (max {size} docs)")
    
    def term_query(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """
        Búsqueda exacta de un término en un campo específico.
        
        Args:
            field: Campo donde buscar
            value: Valor exacto a buscar
            
        Returns:
            list: Lista de documentos encontrados
        """
        query = {
            "query": {
                "term": {field: value}
            }
        }
        return self._execute_query(query, f"Term Query: {field}='{value}'")
    
    def match_query(self, field: str, text: str, source_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Búsqueda dinámica con análisis lingüístico (relevancia).
        
        Args:
            field: Campo donde buscar
            text: Texto a buscar
            source_fields: Campos a incluir en los resultados
            
        Returns:
            list: Lista de documentos encontrados con score de relevancia
        """
        query = {
            "query": {"match": {field: text}}
        }
        
        if source_fields:
            query["_source"] = source_fields
        
        return self._execute_query(query, f"Match Query: {field}='{text}'", include_score=True)
    
    def range_query(self, field: str, gte: Optional[str] = None, lte: Optional[str] = None, 
                   source_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Búsqueda por rango (ideal para fechas o números).
        
        Args:
            field: Campo donde aplicar el rango
            gte: Mayor o igual que (greater than or equal)
            lte: Menor o igual que (less than or equal)
            source_fields: Campos a incluir en los resultados
            
        Returns:
            list: Lista de documentos encontrados
        """
        range_conditions = {}
        if gte:
            range_conditions["gte"] = gte
        if lte:
            range_conditions["lte"] = lte
        
        query = {
            "query": {"range": {field: range_conditions}}
        }
        
        if source_fields:
            query["_source"] = source_fields
        
        return self._execute_query(query, f"Range Query: {field} [{gte} - {lte}]")
    
    def bool_query(self, must: Optional[List[Dict]] = None, filter_terms: Optional[List[Dict]] = None, 
                  should: Optional[List[Dict]] = None, source_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Búsqueda booleana compuesta (combina múltiples condiciones).
        
        Args:
            must: Condiciones que DEBEN cumplirse (afectan score)
            filter_terms: Condiciones de filtro (no afectan score)
            should: Condiciones que DEBERÍAN cumplirse (opcionales)
            source_fields: Campos a incluir en los resultados
            
        Returns:
            list: Lista de documentos encontrados
        """
        bool_conditions = {}
        
        if must:
            bool_conditions["must"] = must
        if filter_terms:
            bool_conditions["filter"] = filter_terms
        if should:
            bool_conditions["should"] = should
        
        query = {
            "query": {"bool": bool_conditions}
        }
        
        if source_fields:
            query["_source"] = source_fields
        
        return self._execute_query(query, "Bool Query (consulta compuesta)", include_score=True)
    
    def aggregation_query(self, agg_field: str, agg_name: str = "aggregation") -> List[Dict[str, Any]]:
        """
        Consulta con agregaciones (para crear filtros y estadísticas).
        
        Args:
            agg_field: Campo sobre el cual agregar
            agg_name: Nombre de la agregación
            
        Returns:
            list: Resultados de la agregación
        """
        try:
            query = {
                "size": 0,  # No necesitamos documentos, solo agregaciones
                "aggs": {
                    agg_name: {
                        "terms": {"field": agg_field}
                    }
                }
            }
            
            logger.info("Ejecutando Aggregation Query: campo '%s'", agg_field)
            response = self.es.search(index=self.index_name, body=query)
            
            buckets = response['aggregations'][agg_name]['buckets']
            
            logger.info("✓ Agregación completada: %d categorías", len(buckets))
            
            results = [
                {'key': bucket['key'], 'count': bucket['doc_count']}
                for bucket in buckets
            ]
            
            for result in results:
                logger.info("  - %s: %d documentos", result['key'], result['count'])
            
            return results
            
        except Exception as e:
            logger.error("Error en Aggregation Query: %s", e)
            raise
    
    def multi_match_query(self, text: str, fields: List[str], source_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Búsqueda en múltiples campos simultáneamente.
        
        Args:
            text: Texto a buscar
            fields: Lista de campos donde buscar
            source_fields: Campos a incluir en los resultados
            
        Returns:
            list: Lista de documentos encontrados
        """
        query = {
            "query": {
                "multi_match": {
                    "query": text,
                    "fields": fields
                }
            }
        }
        
        if source_fields:
            query["_source"] = source_fields
        
        return self._execute_query(query, f"Multi Match Query: '{text}' en {fields}", include_score=True)
    
    def _format_results(self, hits: List[Dict], include_score: bool = False) -> List[Dict[str, Any]]:
        """
        Formatea los resultados de una consulta.
        
        Args:
            hits: Resultados de Elasticsearch
            include_score: Si incluir el score de relevancia
            
        Returns:
            list: Lista de documentos formateados
        """
        results = []
        for hit in hits:
            result = {
                'id': hit['_id'],
                'data': hit['_source']
            }
            if include_score:
                result['score'] = hit['_score']
            results.append(result)
        
        return results
