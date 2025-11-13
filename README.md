# 📚 Elasticsearch - Proyecto Python

Proyecto completo de Python para trabajar con Elasticsearch, implementando indexación de documentos, configuración de índices y consultas avanzadas utilizando Query DSL.

## 🎯 Características

- ✅ Conexión segura a Elasticsearch Cloud
- ✅ Gestión completa de índices con mapping personalizado
- ✅ Analizador lingüístico para español (tokenización, stemming, stop words)
- ✅ Indexación individual y masiva (bulk)
- ✅ Múltiples tipos de consultas (Match All, Term, Match, Range, Bool, Aggregation)
- ✅ Sistema de logging con colores
- ✅ Manejo de errores robusto
- ✅ Configuración mediante variables de entorno
- ✅ Arquitectura modular y escalable

## 📁 Estructura del Proyecto

```
elasticsearch-proyecto/
├── src/
│   ├── __init__.py
│   ├── config.py                  # Configuración y variables de entorno
│   ├── logger.py                  # Sistema de logging personalizado
│   ├── elasticsearch_client.py    # Cliente de conexión a Elasticsearch
│   ├── index_manager.py           # Gestión de índices
│   ├── document_indexer.py        # Indexación de documentos
│   └── query_builder.py           # Constructor de consultas
├── data/
│   └── cuentos_ejemplo.json       # Datos de ejemplo
├── logs/
│   └── elasticsearch.log          # Archivo de logs
├── tests/
│   └── (tests unitarios)
├── main.py                        # Archivo principal de demostración
├── requirements.txt               # Dependencias del proyecto
├── .env.example                   # Ejemplo de variables de entorno
├── .gitignore
└── README.md                      # Este archivo
```

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```powershell
cd C:\elasticsearch-proyecto
```

### 2. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env`:

```powershell
Copy-Item .env.example .env
```

Edita el archivo `.env` y completa tus credenciales de Elasticsearch:

```ini
ELASTIC_CLOUD_ID=tu_cloud_id_aqui
ELASTIC_API_KEY=tu_api_key_aqui
INDEX_NAME=index_cuentos
LOG_LEVEL=INFO
```

#### ¿Cómo obtener las credenciales?

1. **ELASTIC_CLOUD_ID**: 
   - Inicia sesión en https://cloud.elastic.co
   - Ve a tu deployment
   - Copia el "Cloud ID"

2. **ELASTIC_API_KEY**:
   - En tu deployment, ve a "Management" → "API Keys"
   - Crea una nueva API Key
   - Copia la clave generada

## 💻 Uso

### Ejecutar demostración completa

```powershell
python main.py
```

Este comando ejecutará una demostración completa que incluye:

1. ✅ Conexión a Elasticsearch
2. ✅ Creación del índice con mapping
3. ✅ Indexación de 10 documentos de ejemplo
4. ✅ Ejecución de 7 tipos de consultas diferentes
5. ✅ Visualización de resultados

### Uso de módulos individuales

#### Conexión a Elasticsearch

```python
from src.elasticsearch_client import ElasticsearchClient

# Crear cliente y conectar
es_client = ElasticsearchClient()
es_client.connect()

# Verificar salud del cluster
es_client.check_health()

# Obtener cliente para operaciones
client = es_client.get_client()
```

#### Gestión de índices

```python
from src.index_manager import IndexManager

# Crear gestor de índices
index_manager = IndexManager(client)

# Crear índice con mapping
index_manager.create_index(delete_if_exists=True)

# Verificar si existe
if index_manager.index_exists():
    print("El índice existe")

# Obtener información del índice
info = index_manager.get_index_info()
```

#### Indexación de documentos

```python
from src.document_indexer import DocumentIndexer

# Crear indexador
indexer = DocumentIndexer(client)

# Indexar un solo documento
documento = {
    "autor": "Juan Pérez",
    "tipo_documento": "fantastico",
    "texto": "Érase una vez...",
    "fecha": "2024-11-12"
}
indexer.index_single_document(documento)

# Indexación masiva
documentos = [doc1, doc2, doc3, ...]
success, errors = indexer.index_bulk_documents(documentos)

# Contar documentos
count = indexer.count_documents()
```

#### Consultas

```python
from src.query_builder import QueryBuilder

# Crear constructor de consultas
query = QueryBuilder(client)

# 1. Match All (todos los documentos)
results = query.match_all(size=100)

# 2. Term Query (búsqueda exacta)
results = query.term_query("tipo_documento", "terror")

# 3. Match Query (búsqueda con relevancia)
results = query.match_query("texto", "dragón mágico")

# 4. Range Query (búsqueda por rango)
results = query.range_query("fecha", 
                           gte="2024-01-01", 
                           lte="2024-12-31")

# 5. Bool Query (búsqueda compuesta)
results = query.bool_query(
    must=[{"match": {"texto": "reino"}}],
    filter_terms=[{"term": {"tipo_documento": "fantastico"}}]
)

# 6. Aggregation Query (estadísticas)
results = query.aggregation_query("tipo_documento")

# 7. Multi Match Query (búsqueda en varios campos)
results = query.multi_match_query("texto buscar", 
                                  ["autor", "texto"])
```

## 🔍 Tipos de Consultas Implementadas

### A. Match All Query
Devuelve todos los documentos del índice.
```python
results = query.match_all(size=100)
```

### B. Term Query
Búsqueda exacta sin análisis lingüístico.
```python
results = query.term_query("tipo_documento", "terror")
```

### C. Match Query
Búsqueda con análisis lingüístico (tokenización, stemming).
```python
results = query.match_query("texto", "dragón bosque mágico")
```

### D. Range Query
Búsqueda por rangos (fechas, números).
```python
results = query.range_query("fecha", 
                           gte="2024-04-01", 
                           lte="2024-07-31")
```

### E. Bool Query
Combina múltiples condiciones (`must`, `filter`, `should`).
```python
results = query.bool_query(
    must=[{"match": {"texto": "reino"}}],
    filter_terms=[{"term": {"tipo_documento": "fantastico"}}]
)
```

### F. Aggregation Query
Genera estadísticas y conteos para filtros.
```python
results = query.aggregation_query("tipo_documento")
# Resultado: {'fantastico': 3, 'terror': 2, 'infantil': 3, ...}
```

### G. Multi Match Query
Búsqueda en múltiples campos simultáneamente.
```python
results = query.multi_match_query("buscar", ["autor", "texto"])
```

## 📊 Configuración del Mapping

El índice está configurado con:

### Analizador Español
- **Tokenizer**: standard
- **Filters**:
  - lowercase (minúsculas)
  - asciifolding (elimina acentos)
  - spanish_stop (elimina palabras vacías)
  - spanish_stemmer (lematización)

### Campos del Documento

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `autor` | keyword | Búsqueda exacta del autor |
| `tipo_documento` | keyword | Categoría del documento |
| `fecha` | date | Fecha en formato YYYY-MM-DD |
| `texto` | text | Contenido principal con analizador español |

## 🔧 Mejores Prácticas Implementadas

### 1. Arquitectura Modular
- Separación de responsabilidades en módulos independientes
- Cada módulo tiene una función específica

### 2. Configuración Centralizada
- Variables de entorno mediante `.env`
- Clase `Config` para gestión centralizada

### 3. Logging Estructurado
- Logs con colores en consola
- Logs persistentes en archivo
- Diferentes niveles (DEBUG, INFO, WARNING, ERROR)

### 4. Manejo de Errores
- Try-catch en todas las operaciones críticas
- Mensajes de error descriptivos
- Validación de datos antes de indexar

### 5. Validación de Datos
- Verificación de campos requeridos
- Validación de formatos (fechas)
- Mensajes de error claros

### 6. Documentación
- Docstrings en todas las funciones y clases
- Comentarios explicativos
- README completo con ejemplos

## 📝 Requisitos del Sistema

- Python 3.8 o superior
- Elasticsearch 8.11.0 o superior
- Conexión a internet (para Elasticsearch Cloud)
- Sistema operativo: Windows, Linux o macOS

## 🐛 Solución de Problemas

### Error de conexión

```
ConnectionError: No se puede conectar al servidor
```

**Solución**: Verifica que el `ELASTIC_CLOUD_ID` sea correcto y que tengas conexión a internet.

### Error de autenticación

```
AuthenticationException: API Key inválida
```

**Solución**: Verifica que el `ELASTIC_API_KEY` esté correctamente configurado en el archivo `.env`.

### Módulo no encontrado

```
ModuleNotFoundError: No module named 'elasticsearch'
```

**Solución**: Instala las dependencias con `pip install -r requirements.txt`.

### Error al crear índice

```
El índice ya existe
```

**Solución**: Usa `create_index(delete_if_exists=True)` para eliminar el índice anterior.

## 📚 Recursos Adicionales

- [Documentación oficial de Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)
- [Query DSL Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
- [Text Analysis](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html)

## 🤝 Contribuciones

Este proyecto fue desarrollado con fines educativos para demostrar las capacidades de Elasticsearch con Python.

## 📄 Licencia

MIT License - Libre para uso educativo y comercial.

## ✨ Características Avanzadas

### Índice Invertido
Elasticsearch utiliza un índice invertido que mapea términos a documentos, permitiendo búsquedas extremadamente rápidas.

### Tokenización
El texto se divide en tokens (palabras) que luego se normalizan y procesan.

### Lematización (Stemming)
Reduce las palabras a su raíz: "corriendo" → "corr", "corredor" → "corr".

### Stop Words
Elimina palabras comunes sin valor semántico: "el", "la", "de", "en".

### Score de Relevancia
Cada resultado tiene un score que indica qué tan relevante es para la búsqueda.

## 🎓 Conceptos Clave

1. **Índice**: Colección de documentos similar a una base de datos
2. **Documento**: Unidad básica de información (similar a un registro)
3. **Mapping**: Esquema que define tipos de campos
4. **Analyzer**: Procesa texto para búsqueda (tokenización, normalización)
5. **Query DSL**: Lenguaje de consultas JSON de Elasticsearch
6. **Aggregations**: Análisis y estadísticas sobre los datos

---

**Proyecto desarrollado para demostración de Elasticsearch con Python** 🚀

Para más información o soporte, consulta la documentación oficial de Elasticsearch.
