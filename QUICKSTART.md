# Guía de Inicio Rápido - Elasticsearch Python

## 🚀 Pasos para ejecutar el proyecto

### 1. Abrir el proyecto en VS Code
```powershell
cd C:\elasticsearch-proyecto
code .
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

### 4. Configurar credenciales

Copia `.env.example` a `.env`:
```powershell
Copy-Item .env.example .env
```

Edita `.env` y agrega tus credenciales:
```ini
ELASTIC_CLOUD_ID=tu_cloud_id
ELASTIC_API_KEY=tu_api_key
INDEX_NAME=index_cuentos
LOG_LEVEL=INFO
```

### 5. Ejecutar el proyecto
```powershell
python main.py
```

## 📋 Obtener credenciales de Elasticsearch

1. Ve a https://cloud.elastic.co
2. Inicia sesión o crea una cuenta gratuita
3. Crea un nuevo deployment (Free tier disponible)
4. Copia el **Cloud ID** desde el dashboard
5. Ve a Management → Stack Management → API Keys
6. Crea una nueva API Key y cópiala

## ✅ Verificación

Si todo está configurado correctamente, verás:
- ✓ Conexión exitosa a Elasticsearch
- ✓ Índice creado con éxito
- ✓ 10 documentos indexados
- ✓ Resultados de 7 tipos de consultas

## 🆘 Problemas comunes

### Error: "Unable to import elasticsearch"
```powershell
pip install --upgrade elasticsearch==8.11.0
```

### Error: "ELASTIC_CLOUD_ID no está configurado"
Verifica que el archivo `.env` existe y tiene las credenciales correctas.

### Error de conexión
- Verifica tu conexión a internet
- Confirma que el Cloud ID es correcto
- Revisa que la API Key tenga permisos suficientes

## 📚 Recursos

- README.md - Documentación completa
- data/cuentos_ejemplo.json - Datos de ejemplo
- logs/elasticsearch.log - Logs de ejecución
