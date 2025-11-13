"""
Ejemplo 1: Búsqueda simple por texto
"""
from src.elasticsearch_client import ElasticsearchClient
from src.query_builder import QueryBuilder

# Conectar
es_client = ElasticsearchClient()
es_client.connect()
query = QueryBuilder(es_client.get_client())

# Buscar documentos que contengan "dragón"
results = query.match_query("texto", "dragón")

print(f"\n{'='*60}")
print(f"BÚSQUEDA: 'dragón'")
print(f"{'='*60}")
print(f"Encontrados: {len(results)} documentos\n")

for i, r in enumerate(results, 1):
    data = r['data']
    score = r.get('score', 0)
    print(f"{i}. Score: {score:.2f}")
    print(f"   Autor: {data['autor']}")
    print(f"   Tipo: {data['tipo_documento']}")
    print(f"   Texto: {data['texto'][:100]}...")
    print()

es_client.disconnect()
