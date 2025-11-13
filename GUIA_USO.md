# 🚀 Guía de Uso - Elasticsearch Python

## 📋 Ejecución Rápida

### Ejecutar demostración completa
```powershell
cd C:\elasticsearch-proyecto
.\venv\Scripts\Activate.ps1
python main.py
```

Esto ejecutará automáticamente:
- Conexión a Elasticsearch
- Creación del índice
- Indexación de 10 documentos de ejemplo
- 7 tipos de consultas diferentes

---

## 💻 Uso de Módulos Individuales

### 1️⃣ Conectar a Elasticsearch

```python
from src.elasticsearch_client import ElasticsearchClient

# Crear cliente y conectar
es_client = ElasticsearchClient()
es_client.connect()

# Obtener cliente para usar
client = es_client.get_client()
```

### 2️⃣ Crear un Índice

```python
from src.index_manager import IndexManager

# Crear gestor de índices
index_manager = IndexManager(client)

# Crear índice (elimina si existe)
index_manager.create_index(delete_if_exists=True)

# Verificar si existe
if index_manager.index_exists():
    print("✓ Índice creado")
```

### 3️⃣ Indexar Documentos

#### Indexar un solo documento
```python
from src.document_indexer import DocumentIndexer

indexer = DocumentIndexer(client)

documento = {
    "autor": "Juan Pérez",
    "tipo_documento": "fantastico",
    "texto": "Érase una vez en un reino lejano...",
    "fecha": "2024-11-12"
}

indexer.index_single_document(documento)
```

#### Indexar múltiples documentos (bulk)
```python
documentos = [
    {
        "autor": "Maria García",
        "tipo_documento": "infantil",
        "texto": "El patito feo nadaba en el lago...",
        "fecha": "2024-11-10"
    },
    {
        "autor": "Carlos López",
        "tipo_documento": "terror",
        "texto": "La noche era oscura y tenebrosa...",
        "fecha": "2024-11-11"
    }
    # ... más documentos
]

success, errors = indexer.index_bulk_documents(documentos)
print(f"Documentos indexados: {success}")
```

### 4️⃣ Realizar Consultas

```python
from src.query_builder import QueryBuilder

query = QueryBuilder(client)
```

#### A. Ver todos los documentos
```python
results = query.match_all(size=100)

for result in results:
    print(f"ID: {result['id']}")
    print(f"Autor: {result['data']['autor']}")
    print(f"Texto: {result['data']['texto'][:50]}...")
```

#### B. Búsqueda exacta (Term Query)
```python
# Buscar documentos de tipo "terror"
results = query.term_query("tipo_documento", "terror")

# Buscar por autor específico
results = query.term_query("autor", "Maria García")
```

#### C. Búsqueda con relevancia (Match Query)
```python
# Busca en el texto con análisis lingüístico
results = query.match_query("texto", "dragón bosque mágico")

for result in results:
    print(f"Score: {result['score']} - {result['data']['autor']}")
```

#### D. Búsqueda por rango de fechas
```python
results = query.range_query(
    "fecha",
    gte="2024-01-01",  # Mayor o igual
    lte="2024-12-31"   # Menor o igual
)
```

#### E. Búsqueda combinada (Bool Query)
```python
# Buscar documentos que contengan "reino" Y sean de tipo "fantastico"
results = query.bool_query(
    must=[{"match": {"texto": "reino"}}],
    filter_terms=[{"term": {"tipo_documento": "fantastico"}}]
)
```

#### F. Estadísticas y conteos (Aggregation)
```python
# Contar documentos por tipo
results = query.aggregation_query("tipo_documento")

for item in results:
    print(f"{item['key']}: {item['count']} documentos")
```

#### G. Buscar en múltiples campos
```python
# Buscar "Maria dragon" en autor y texto
results = query.multi_match_query(
    "Maria dragon",
    ["autor", "texto"]
)
```

---

## 🔧 Scripts Útiles

### Script de prueba rápida
```python
# test_rapido.py
from src.elasticsearch_client import ElasticsearchClient
from src.query_builder import QueryBuilder

# Conectar
es_client = ElasticsearchClient()
es_client.connect()

# Buscar
query = QueryBuilder(es_client.get_client())
results = query.match_query("texto", "tu búsqueda aquí")

# Mostrar resultados
for r in results:
    print(f"{r['data']['autor']}: {r['data']['texto'][:80]}...")
```

### Contar documentos
```python
from src.document_indexer import DocumentIndexer

indexer = DocumentIndexer(client)
total = indexer.count_documents()
print(f"Total de documentos: {total}")
```

### Eliminar un documento
```python
indexer.delete_document(doc_id="5")
```

### Obtener un documento específico
```python
doc = indexer.get_document_by_id("1")
print(doc)
```

---

## 📝 Ejemplos Prácticos

### Ejemplo 1: Buscar cuentos de terror después de julio 2024
```python
results = query.bool_query(
    must=[{"term": {"tipo_documento": "terror"}}],
    filter_terms=[{"range": {"fecha": {"gte": "2024-07-01"}}}]
)
```

### Ejemplo 2: Buscar palabra clave en todos los campos
```python
results = query.multi_match_query(
    "dragón",
    ["autor", "texto", "tipo_documento"]
)
```

### Ejemplo 3: Top 5 documentos más relevantes
```python
results = query.match_query("texto", "reino mágico aventura")
top_5 = results[:5]

for i, r in enumerate(top_5, 1):
    print(f"{i}. {r['data']['autor']} - Score: {r['score']:.2f}")
```

---

## 🔍 Consejos de Búsqueda

### ✅ **Term Query** (Búsqueda exacta)
- Usa para: tipo_documento, autor (campos keyword)
- Ejemplo: `"terror"`, `"Maria Garcia"`
- **No** aplica análisis lingüístico

### ✅ **Match Query** (Búsqueda inteligente)
- Usa para: texto (campos text)
- Ejemplo: `"dragón bosque mágico"`
- **Sí** aplica stemming, stop words
- Retorna con score de relevancia

### ✅ **Range Query**
- Usa para: fechas, números
- Operadores: `gte`, `lte`, `gt`, `lt`

### ✅ **Bool Query**
- Combina múltiples condiciones
- `must`: DEBE cumplirse (afecta score)
- `filter`: DEBE cumplirse (NO afecta score)
- `should`: OPCIONAL (afecta score si se cumple)

---

## 📊 Ver Logs

Los logs se guardan en:
```
logs/elasticsearch.log
```

Ver en tiempo real:
```powershell
Get-Content logs/elasticsearch.log -Tail 50 -Wait
```

---

## ⚙️ Configuración

Edita el archivo `.env` para cambiar:

```ini
# Cambiar nombre del índice
INDEX_NAME=mi_nuevo_indice

# Cambiar nivel de logs
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

---

## 🔄 Reiniciar desde Cero

```python
from src.index_manager import IndexManager

index_manager = IndexManager(client)

# Eliminar índice existente
index_manager.delete_index()

# Crear nuevo índice
index_manager.create_index()

# Volver a indexar documentos
# ...
```

---

## 🆘 Solución de Problemas

### Error: "No hay conexión"
```powershell
# Verifica la configuración
python test_connection.py
```

### Error: "Índice no existe"
```python
# Crear el índice primero
index_manager.create_index()
```

### Ver información del índice
```python
info = index_manager.get_index_info()
print(f"Documentos: {info['doc_count']}")
```

---

## 📚 Recursos Adicionales

- `README.md` - Documentación completa del proyecto
- `QUICKSTART.md` - Guía de inicio rápido
- `main.py` - Ejemplo completo de todas las funcionalidades
- `test_connection.py` - Script de diagnóstico

---

## 🎯 Próximos Pasos

1. **Personaliza los datos**: Edita `data/cuentos_ejemplo.json`
2. **Crea tus propias consultas**: Modifica `main.py`
3. **Agrega más campos**: Actualiza el mapping en `index_manager.py`
4. **Integra en tu aplicación**: Importa los módulos desde `src/`

---

**¡Listo para usar Elasticsearch! 🚀**

Para más ayuda, consulta la documentación oficial:
https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
