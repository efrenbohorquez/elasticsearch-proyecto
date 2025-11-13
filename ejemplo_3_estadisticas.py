"""
Ejemplo 3: Estadísticas de documentos
"""
from src.elasticsearch_client import ElasticsearchClient
from src.query_builder import QueryBuilder
from src.document_indexer import DocumentIndexer

# Conectar
es_client = ElasticsearchClient()
es_client.connect()

# Obtener estadísticas
indexer = DocumentIndexer(es_client.get_client())
total = indexer.count_documents()

query = QueryBuilder(es_client.get_client())
stats = query.aggregation_query("tipo_documento")

print(f"\n{'='*60}")
print(f"ESTADÍSTICAS DEL ÍNDICE")
print(f"{'='*60}")
print(f"\nTotal de documentos: {total}")
print(f"\nDistribución por tipo:")
print("-" * 40)

for item in stats:
    tipo = item['key']
    count = item['count']
    porcentaje = (count / total * 100) if total > 0 else 0
    barra = "█" * int(porcentaje / 5)
    print(f"{tipo:15} {barra} {count:2} ({porcentaje:.1f}%)")

print()

es_client.disconnect()
