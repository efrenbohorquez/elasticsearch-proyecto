# 🚀 Guía de Despliegue en Render

Esta guía te ayudará a desplegar tu proyecto de Elasticsearch en Render.

## 📋 Prerrequisitos

1. ✅ Cuenta en [Render](https://render.com) (gratuita)
2. ✅ Cuenta en [GitHub](https://github.com) con tu repositorio
3. ✅ Credenciales de Elasticsearch Cloud (API Key o Usuario/Contraseña)
4. ✅ Repositorio actualizado en GitHub

## 📦 Archivos de Configuración

Los archivos necesarios ya están creados:
- ✅ `render.yaml` - Configuración de Render (Worker Service)
- ✅ `runtime.txt` - Versión de Python (3.11.9)
- ✅ `requirements.txt` - Dependencias del proyecto

## 🔧 Paso 1: Verificar Repositorio GitHub

Asegúrate de que todos los cambios estén en GitHub:

```powershell
git status
git add .
git commit -m "Preparar despliegue en Render"
git push origin main
cd C:\elasticsearch-proyecto
git add render.yaml runtime.txt DEPLOY_RENDER.md
git commit -m "Add Render deployment configuration"
git push origin main
```

## 🌐 Paso 2: Crear Servicio en Render

### Opción A: Despliegue con Blueprint (Recomendado)

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **"New +"** → **"Blueprint"**
3. Conecta tu repositorio de GitHub: `efrenbohorquez/elasticsearch-proyecto`
4. Render detectará automáticamente el archivo `render.yaml`
5. Click en **"Apply"**

### Opción B: Despliegue Manual

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio: `efrenbohorquez/elasticsearch-proyecto`
4. Configura:
   - **Name**: `elasticsearch-proyecto`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. Click en **"Create Web Service"**

## 🔐 Paso 3: Configurar Variables de Entorno

En la configuración de tu servicio en Render:

1. Ve a **"Environment"** en el menú lateral
2. Agrega las siguientes variables:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `ELASTIC_CLOUD_ID` | `tu_cloud_id` | ID de tu deployment en Elastic Cloud |
| `ELASTIC_API_KEY` | `tu_api_key` | API Key de Elasticsearch |
| `INDEX_NAME` | `index_cuentos` | Nombre del índice |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

### ¿Dónde obtener las credenciales?

#### ELASTIC_CLOUD_ID
1. Ve a https://cloud.elastic.co
2. Selecciona tu deployment
3. En "Cloud ID", copia el valor completo

**O usa la URL directa:**
```
https://my-elasticsearch-project-a1e563.es.us-central1.gcp.elastic.cloud
```

#### ELASTIC_API_KEY
1. En tu deployment, ve a **"Management"** → **"Stack Management"**
2. Click en **"API Keys"**
3. Click en **"Create API key"**
4. Dale un nombre: `render-deployment`
5. Copia la clave generada

3. Click en **"Save Changes"**

## 🎯 Paso 4: Desplegar

Render comenzará automáticamente el despliegue:

1. **Build**: Instala las dependencias (`pip install`)
2. **Deploy**: Ejecuta tu aplicación
3. **Live**: Tu servicio estará disponible

### Monitorear el Despliegue

- Ve a la pestaña **"Logs"** para ver el progreso
- Deberías ver:
  ```
  ✅ Conexión exitosa a Elasticsearch
  ✅ Índice creado correctamente
  ✅ Documentos indexados
  ✅ Consultas ejecutadas
  ```

## 📊 Paso 5: Verificar el Despliegue

### Ver Logs en Tiempo Real

```bash
# En Render Dashboard → Logs
```

Deberías ver:
- ✅ Conexión a Elasticsearch establecida
- ✅ Versión de Elasticsearch: 8.11.0
- ✅ Índice `index_cuentos` creado
- ✅ 10 documentos indexados
- ✅ Consultas ejecutadas correctamente

### Acceder a tu Aplicación

Render te proporcionará una URL:
```
https://elasticsearch-proyecto.onrender.com
```

## 🔄 Actualizaciones Automáticas

Render se actualizará automáticamente cuando hagas `git push`:

```powershell
# Hacer cambios en tu código
git add .
git commit -m "Actualizar funcionalidad"
git push origin main

# Render detectará el push y desplegará automáticamente
```

## 🆓 Plan Gratuito de Render

### Limitaciones del Plan Free

- ⏱️ El servicio se duerme después de 15 minutos de inactividad
- 🔄 Tarda ~30 segundos en despertar al recibir una petición
- 💾 750 horas/mes de uso gratuito
- 🌐 Dominio compartido: `*.onrender.com`

### Para Producción

Si necesitas un servicio 24/7, considera:
- **Starter Plan**: $7/mes
- **Standard Plan**: $25/mes
- Sin tiempo de inactividad
- Dominios personalizados

## 🔧 Configuración Avanzada

### Usar Web Service en lugar de Worker

Si quieres que el servicio esté siempre activo y responda a HTTP:

1. Crea un archivo `app.py` con Flask:

```python
from flask import Flask, jsonify
from main import main as run_elasticsearch

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "project": "Elasticsearch Python"
    })

@app.route('/run')
def run():
    try:
        run_elasticsearch()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
```

2. Actualiza `requirements.txt`:
```
elasticsearch==8.11.0
python-dotenv==1.0.0
requests==2.31.0
colorama==0.4.6
pytest==7.4.3
flask==3.0.0
gunicorn==21.2.0
```

3. Actualiza `render.yaml`:
```yaml
services:
  - type: web
    name: elasticsearch-proyecto
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: ELASTIC_CLOUD_ID
        sync: false
      - key: ELASTIC_API_KEY
        sync: false
      - key: INDEX_NAME
        value: index_cuentos
```

### Configurar Cron Jobs

Para ejecutar tareas periódicas:

```yaml
services:
  - type: cron
    name: elasticsearch-sync
    runtime: python
    schedule: "0 */6 * * *"  # Cada 6 horas
    buildCommand: pip install -r requirements.txt
    startCommand: python sync_script.py
```

## 🐛 Solución de Problemas

### Error: "Build failed"

**Problema**: Dependencias no se instalan correctamente.

**Solución**:
1. Verifica que `requirements.txt` esté actualizado
2. Asegúrate de que Python 3.11+ esté en `runtime.txt`

### Error: "Unable to authenticate"

**Problema**: Credenciales de Elasticsearch incorrectas.

**Solución**:
1. Verifica las variables de entorno en Render
2. Regenera tu API Key en Elastic Cloud
3. Actualiza `ELASTIC_API_KEY` en Render

### Error: "Module not found"

**Problema**: Falta una dependencia.

**Solución**:
```powershell
# Actualizar requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Servicio se duerme constantemente

**Solución**: Usa un servicio de ping externo o actualiza al plan Starter.

## 📱 Monitoreo y Alertas

### Configurar Notificaciones

1. En Render Dashboard → Service → **"Settings"**
2. En **"Notifications"**, conecta:
   - Slack
   - Discord
   - Email

### Ver Métricas

- **CPU Usage**: Dashboard → Metrics
- **Memory**: Dashboard → Metrics
- **Response Time**: Dashboard → Metrics

## 🔒 Seguridad

### Mejores Prácticas

1. ✅ **Nunca** subas archivos `.env` a GitHub
2. ✅ Usa variables de entorno en Render
3. ✅ Regenera API Keys periódicamente
4. ✅ Limita los permisos de la API Key
5. ✅ Usa HTTPS siempre (Render lo hace por defecto)

### Limitar Acceso a IP

En Elastic Cloud:
1. Ve a **"Security"** → **"IP Filtering"**
2. Agrega la IP de Render (disponible en los logs)

## 📚 Recursos Adicionales

- [Documentación de Render](https://render.com/docs)
- [Render Python Guide](https://render.com/docs/deploy-flask)
- [Elasticsearch Cloud](https://cloud.elastic.co)
- [GitHub Actions para CI/CD](https://github.com/features/actions)

## ✅ Checklist de Despliegue

- [ ] Cuenta en Render creada
- [ ] Repositorio en GitHub actualizado
- [ ] `render.yaml` configurado
- [ ] Variables de entorno configuradas
- [ ] API Key de Elasticsearch creada
- [ ] Servicio desplegado en Render
- [ ] Logs verificados sin errores
- [ ] Documentos indexados correctamente
- [ ] Consultas funcionando

---

**¡Tu proyecto Elasticsearch ahora está en la nube!** 🎉

Para más ayuda, consulta la [documentación de Render](https://render.com/docs) o el [soporte de Elastic](https://www.elastic.co/support).
