"""
Ejemplo 2: Búsqueda por tipo y fecha
"""
from src.elasticsearch_client import ElasticsearchClient
from src.query_builder import QueryBuilder

# Conectar
es_client = ElasticsearchClient()
es_client.connect()
query = QueryBuilder(es_client.get_client())

# Buscar cuentos de terror después de julio 2024
results = query.bool_query(
    must=[{"term": {"tipo_documento": "terror"}}],
    filter_terms=[{"range": {"fecha": {"gte": "2024-07-01"}}}]
)

print(f"\n{'='*60}")
print(f"BÚSQUEDA: Cuentos de TERROR desde Julio 2024")
print(f"{'='*60}")
print(f"Encontrados: {len(results)} documentos\n")

for i, r in enumerate(results, 1):
    data = r['data']
    print(f"{i}. {data['autor']} ({data['fecha']})")
    print(f"   {data['texto'][:150]}...")
    print()

es_client.disconnect()
