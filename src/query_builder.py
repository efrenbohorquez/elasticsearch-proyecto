"""
Módulo de consultas a Elasticsearch
Implementa diferentes tipos de búsquedas usando Query DSL.
"""
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)


class QueryBuilder:
    """Constructor de consultas para Elasticsearch."""
    
    def __init__(self, es_client):
        """
        Inicializa el constructor de consultas.
        
        Args:
            es_client: Cliente de Elasticsearch conectado
        """
        self.es = es_client
        self.index_name = Config.INDEX_NAME
    
    def match_all(self, size=100):
        """
        Consulta que devuelve todos los documentos.
        
        Args:
            size: Número máximo de documentos a devolver
            
        Returns:
            list: Lista de documentos encontrados
        """
        try:
            query = {
                "query": {
                    "match_all": {}
                },
                "size": size
            }
            
            logger.info(f"Ejecutando consulta Match All (max {size} docs)...")
            response = self.es.search(index=self.index_name, body=query)
            
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            logger.info(f"✓ Encontrados {total} documentos (mostrando {len(hits)})")
            
            return self._format_results(hits)
            
        except Exception as e:
            logger.error(f"Error en consulta Match All: {e}")
            raise
    
    def term_query(self, field, value):
        """
        Búsqueda exacta de un término en un campo específico.
        
        Args:
            field: Campo donde buscar
            value: Valor exacto a buscar
            
        Returns:
            list: Lista de documentos encontrados
        """
        try:
            query = {
                "query": {
                    "term": {
                        field: value
                    }
                }
            }
            
            logger.info(f"Ejecutando Term Query: {field}='{value}'")
            response = self.es.search(index=self.index_name, body=query)
            
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            logger.info(f"✓ Encontrados {total} documentos")
            
            return self._format_results(hits)
            
        except Exception as e:
            logger.error(f"Error en Term Query: {e}")
            raise
    
    def match_query(self, field, text, source_fields=None):
        """
        Búsqueda dinámica con análisis lingüístico (relevancia).
        
        Args:
            field: Campo donde buscar
            text: Texto a buscar
            source_fields: Campos a incluir en los resultados
            
        Returns:
            list: Lista de documentos encontrados con score de relevancia
        """
        try:
            query = {
                "query": {
                    "match": {
                        field: text
                    }
                }
            }
            
            if source_fields:
                query["_source"] = source_fields
            
            logger.info(f"Ejecutando Match Query: {field}='{text}'")
            response = self.es.search(index=self.index_name, body=query)
            
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            logger.info(f"✓ Encontrados {total} documentos con relevancia")
            
            return self._format_results(hits, include_score=True)
            
        except Exception as e:
            logger.error(f"Error en Match Query: {e}")
            raise
    
    def range_query(self, field, gte=None, lte=None, source_fields=None):
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
        try:
            range_conditions = {}
            if gte:
                range_conditions["gte"] = gte
            if lte:
                range_conditions["lte"] = lte
            
            query = {
                "query": {
                    "range": {
                        field: range_conditions
                    }
                }
            }
            
            if source_fields:
                query["_source"] = source_fields
            
            logger.info(f"Ejecutando Range Query: {field} [{gte} - {lte}]")
            response = self.es.search(index=self.index_name, body=query)
            
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            logger.info(f"✓ Encontrados {total} documentos en el rango")
            
            return self._format_results(hits)
            
        except Exception as e:
            logger.error(f"Error en Range Query: {e}")
            raise
    
    def bool_query(self, must=None, filter_terms=None, should=None, source_fields=None):
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
        try:
            bool_conditions = {}
            
            if must:
                bool_conditions["must"] = must
            if filter_terms:
                bool_conditions["filter"] = filter_terms
            if should:
                bool_conditions["should"] = should
            
            query = {
                "query": {
                    "bool": bool_conditions
                }
            }
            
            if source_fields:
                query["_source"] = source_fields
            
            logger.info("Ejecutando Bool Query (consulta compuesta)")
            response = self.es.search(index=self.index_name, body=query)
            
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            logger.info(f"✓ Encontrados {total} documentos")
            
            return self._format_results(hits, include_score=True)
            
        except Exception as e:
            logger.error(f"Error en Bool Query: {e}")
            raise
    
    def aggregation_query(self, agg_field, agg_name="aggregation"):
        """
        Consulta con agregaciones (para crear filtros y estadísticas).
        
        Args:
            agg_field: Campo sobre el cual agregar
            agg_name: Nombre de la agregación
            
        Returns:
            dict: Resultados de la agregación
        """
        try:
            query = {
                "size": 0,  # No necesitamos documentos, solo agregaciones
                "aggs": {
                    agg_name: {
                        "terms": {
                            "field": agg_field
                        }
                    }
                }
            }
            
            logger.info(f"Ejecutando Aggregation Query: campo '{agg_field}'")
            response = self.es.search(index=self.index_name, body=query)
            
            buckets = response['aggregations'][agg_name]['buckets']
            
            logger.info(f"✓ Agregación completada: {len(buckets)} categorías")
            
            results = []
            for bucket in buckets:
                results.append({
                    'key': bucket['key'],
                    'count': bucket['doc_count']
                })
                logger.info(f"  - {bucket['key']}: {bucket['doc_count']} documentos")
            
            return results
            
        except Exception as e:
            logger.error(f"Error en Aggregation Query: {e}")
            raise
    
    def multi_match_query(self, text, fields, source_fields=None):
        """
        Búsqueda en múltiples campos simultáneamente.
        
        Args:
            text: Texto a buscar
            fields: Lista de campos donde buscar
            source_fields: Campos a incluir en los resultados
            
        Returns:
            list: Lista de documentos encontrados
        """
        try:
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
            
            logger.info(f"Ejecutando Multi Match Query: '{text}' en {fields}")
            response = self.es.search(index=self.index_name, body=query)
            
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            logger.info(f"✓ Encontrados {total} documentos")
            
            return self._format_results(hits, include_score=True)
            
        except Exception as e:
            logger.error(f"Error en Multi Match Query: {e}")
            raise
    
    def _format_results(self, hits, include_score=False):
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
