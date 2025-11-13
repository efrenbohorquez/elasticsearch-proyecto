"""
Script de diagnóstico para probar la conexión a Elasticsearch
"""
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import requests

# Cargar variables de entorno
load_dotenv()

ELASTIC_URL = os.getenv('ELASTIC_CLOUD_ID', '')
API_KEY = os.getenv('ELASTIC_API_KEY', '')

print("="*70)
print("DIAGNÓSTICO DE CONEXIÓN A ELASTICSEARCH")
print("="*70)
print(f"\n1. URL configurada: {ELASTIC_URL}")
print(f"2. API Key configurada: {API_KEY[:20]}..." if len(API_KEY) > 20 else f"2. API Key: {API_KEY}")

# Probar conexión directa con requests
print("\n3. Probando conexión HTTP directa...")
try:
    url = ELASTIC_URL if ELASTIC_URL.startswith('http') else f"https://{ELASTIC_URL}"
    headers = {
        'Authorization': f'ApiKey {API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers, timeout=10)
    print(f"   ✓ Respuesta HTTP: {response.status_code}")
    print(f"   ✓ Contenido: {response.text[:200]}")
except Exception as e:
    print(f"   ✗ Error en conexión HTTP: {e}")

# Probar con cliente de Elasticsearch
print("\n4. Probando con cliente de Elasticsearch...")
try:
    es = Elasticsearch(
        url,
        api_key=API_KEY,
        request_timeout=10,
        verify_certs=True
    )
    
    print("   ✓ Cliente creado")
    
    # Intentar ping
    if es.ping():
        print("   ✓ Ping exitoso!")
        info = es.info()
        print(f"   ✓ Versión: {info['version']['number']}")
        print(f"   ✓ Cluster: {info['cluster_name']}")
    else:
        print("   ✗ Ping falló - El servidor no responde")
        
except Exception as e:
    print(f"   ✗ Error con cliente Elasticsearch: {e}")
    print(f"   Tipo de error: {type(e).__name__}")

print("\n" + "="*70)
print("DIAGNÓSTICO COMPLETADO")
print("="*70)
