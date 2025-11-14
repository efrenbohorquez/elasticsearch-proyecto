"""
Archivo principal del proyecto Elasticsearch
Demuestra todas las funcionalidades implementadas.
"""
from typing import List, Dict, Any
from src.elasticsearch_client import ElasticsearchClient
from src.index_manager import IndexManager
from src.document_indexer import DocumentIndexer
from src.query_builder import QueryBuilder
from src.logger import setup_logger
from src.config import Config

logger = setup_logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)

# Constantes
SEPARATOR_WIDTH = 70
MAX_TEXT_PREVIEW = 100


def print_separator(title: str = "") -> None:
    """Imprime un separador visual."""
    print("\n" + "="*SEPARATOR_WIDTH)
    if title:
        print(f"  {title}")
        print("="*SEPARATOR_WIDTH)
    print()


def print_results(results: List[Dict[str, Any]], title: str = "Resultados") -> None:
    """
    Imprime los resultados de una consulta de forma legible.
    
    Args:
        results: Lista de resultados
        title: Título a mostrar
    """
    print(f"\n{title}:")
    print("-" * SEPARATOR_WIDTH)
    
    if not results:
        print("  No se encontraron resultados")
        return
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. ID: {result['id']}")
        
        if 'score' in result:
            print(f"   Score: {result['score']:.2f}")
        
        data = result['data']
        print(f"   Autor: {data.get('autor', 'N/A')}")
        print(f"   Tipo: {data.get('tipo_documento', 'N/A')}")
        print(f"   Fecha: {data.get('fecha', 'N/A')}")
        
        if 'texto' in data:
            texto = data['texto']
            texto_preview = texto[:MAX_TEXT_PREVIEW] + "..." if len(texto) > MAX_TEXT_PREVIEW else texto
            print(f"   Texto: {texto_preview}")


def get_sample_data() -> List[Dict[str, Any]]:
    """Obtiene los datos de ejemplo para indexación."""
    return [
        {
            "autor": "Maria Gonzalez",
            "tipo_documento": "infantil",
            "texto": "Había una vez un pequeño dragón llamado Spark que vivía en un bosque encantado. "
                     "Todos los días exploraba el reino mágico buscando aventuras y nuevos amigos.",
            "fecha": "2024-04-10"
        },
        {
            "autor": "Carlos Ruiz",
            "tipo_documento": "terror",
            "texto": "La casa de la colina abandonada era el lugar más terrorífico de la zona. "
                     "Nadie se atrevía a acercarse después del anochecer, pues extraños sonidos "
                     "resonaban desde su interior.",
            "fecha": "2024-07-01"
        },
        {
            "autor": "Ana Martinez",
            "tipo_documento": "fantastico",
            "texto": "En el reino de las estrellas, donde la magia fluye como ríos de luz, "
                     "vivía una hechicera capaz de controlar el tiempo y el espacio.",
            "fecha": "2024-05-15"
        },
        {
            "autor": "Pedro Lopez",
            "tipo_documento": "infantil",
            "texto": "Los animales del bosque organizaron una gran fiesta para celebrar la llegada "
                     "de la primavera. El oso, el conejo y el zorro bailaban bajo los árboles.",
            "fecha": "2024-03-20"
        },
        {
            "autor": "Laura Sanchez",
            "tipo_documento": "terror",
            "texto": "El reloj de la torre marcaba las doce cuando las sombras comenzaron a moverse. "
                     "Un escalofrío recorrió mi espalda mientras escuchaba pasos acercándose.",
            "fecha": "2024-08-12"
        },
        {
            "autor": "Miguel Torres",
            "tipo_documento": "fantastico",
            "texto": "El dragón guardián del reino había despertado después de mil años. "
                     "Su rugido resonó por toda la tierra, anunciando el retorno de la magia antigua.",
            "fecha": "2024-06-30"
        },
        {
            "autor": "Sofia Ramirez",
            "tipo_documento": "politico",
            "texto": "El reino enfrentaba una crisis sin precedentes. Los consejeros debatían "
                     "sobre las nuevas leyes mientras el pueblo esperaba decisiones justas.",
            "fecha": "2024-09-05"
        },
        {
            "autor": "Diego Morales",
            "tipo_documento": "politico",
            "texto": "La asamblea del reino se reunió para discutir el tratado de paz con las "
                     "tierras vecinas. Era un momento crucial para la diplomacia.",
            "fecha": "2024-10-18"
        },
        {
            "autor": "Elena Vargas",
            "tipo_documento": "infantil",
            "texto": "La pequeña hada Lucía aprendió a volar por primera vez. Con sus alas "
                     "brillantes recorrió todo el jardín encantado lleno de flores mágicas.",
            "fecha": "2024-04-25"
        },
        {
            "autor": "Roberto Diaz",
            "tipo_documento": "fantastico",
            "texto": "En las profundidades del océano mágico existía un reino de sirenas y criaturas "
                     "luminosas. Sus castillos de coral brillaban con luz propia.",
            "fecha": "2024-07-22"
        }
    ]


def demo_conexion() -> ElasticsearchClient:
    """Demuestra la conexión a Elasticsearch."""
    print_separator("1. CONEXIÓN A ELASTICSEARCH")
    
    es_client = ElasticsearchClient()
    es_client.connect()
    es_client.check_health()
    
    return es_client


def demo_creacion_indice(es_client: ElasticsearchClient) -> IndexManager:
    """Demuestra la creación del índice."""
    print_separator("2. CREACIÓN Y CONFIGURACIÓN DEL ÍNDICE")
    
    index_manager = IndexManager(es_client.get_client())
    index_manager.create_index(delete_if_exists=True)
    
    return index_manager


def demo_indexacion(es_client: ElasticsearchClient) -> DocumentIndexer:
    """Demuestra la indexación de documentos."""
    print_separator("3. INDEXACIÓN DE DOCUMENTOS")
    
    indexer = DocumentIndexer(es_client.get_client())
    cuentos = get_sample_data()
    
    # Indexar documentos
    success, errors = indexer.index_bulk_documents(cuentos)
    
    # Contar documentos
    indexer.count_documents()
    
    return indexer


def demo_consultas(es_client: ElasticsearchClient, index_manager: IndexManager) -> None:
    """Demuestra diferentes tipos de consultas."""
    print_separator("4. CONSULTAS Y BÚSQUEDAS")
    
    query = QueryBuilder(es_client.get_client())
    index_manager.refresh_index()
    
    # A. Match All Query
    print("\n📋 A. MATCH ALL QUERY (Todos los documentos)")
    results = query.match_all(size=5)
    print_results(results[:3], "Primeros 3 documentos")
    
    # B. Term Query (Búsqueda exacta)
    print("\n📋 B. TERM QUERY (Búsqueda exacta)")
    results = query.term_query("tipo_documento", "terror")
    print_results(results, "Cuentos de terror")
    
    # C. Match Query (Búsqueda dinámica con relevancia)
    print("\n📋 C. MATCH QUERY (Búsqueda con relevancia)")
    results = query.match_query("texto", "dragón mágico reino", 
                                source_fields=["autor", "tipo_documento"])
    print_results(results, "Búsqueda: 'dragón mágico reino'")
    
    # D. Range Query (Búsqueda por rango de fechas)
    print("\n📋 D. RANGE QUERY (Búsqueda por fecha)")
    results = query.range_query("fecha", 
                                gte="2024-04-01", 
                                lte="2024-07-31",
                                source_fields=["autor", "fecha", "tipo_documento"])
    print_results(results, "Cuentos entre Abril y Julio 2024")
    
    # E. Bool Query (Búsqueda compuesta)
    print("\n📋 E. BOOL QUERY (Búsqueda compuesta)")
    results = query.bool_query(
        must=[{"match": {"texto": "reino"}}],
        filter_terms=[{"term": {"tipo_documento": "fantastico"}}],
        source_fields=["autor", "tipo_documento"]
    )
    print_results(results, "Texto con 'reino' Y tipo 'fantastico'")
    
    # F. Aggregation Query (Estadísticas y filtros)
    print("\n📋 F. AGGREGATION QUERY (Filtros y estadísticas)")
    results = query.aggregation_query("tipo_documento", "cuentos_por_tipo")
    print("\nConteo por tipo de documento:")
    print("-" * SEPARATOR_WIDTH)
    for item in results:
        print(f"  • {item['key']}: {item['count']} documentos")
    
    # G. Multi Match Query
    print("\n📋 G. MULTI MATCH QUERY (Búsqueda en múltiples campos)")
    results = query.multi_match_query(
        "Maria dragon",
        ["autor", "texto"],
        source_fields=["autor", "tipo_documento"]
    )
    print_results(results, "Búsqueda 'Maria dragon' en autor y texto")


def demo_informacion_indice(index_manager: IndexManager) -> None:
    """Muestra información del índice."""
    print_separator("5. INFORMACIÓN DEL ÍNDICE")
    index_manager.get_index_info()


def main() -> None:
    """Función principal que ejecuta todas las demostraciones."""
    try:
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*15 + "ELASTICSEARCH - PROYECTO PYTHON" + " "*22 + "║")
        print("║" + " "*10 + "Demostración completa de funcionalidades" + " "*17 + "║")
        print("╚" + "="*68 + "╝")
        
        # Usar context manager para manejo automático de conexión
        with ElasticsearchClient() as es_client:
            # Creación del índice
            index_manager = demo_creacion_indice(es_client)
            
            # Indexación de documentos
            demo_indexacion(es_client)
            
            # Consultas
            demo_consultas(es_client, index_manager)
            
            # Información del índice
            demo_informacion_indice(index_manager)
        
        # Finalizar
        print_separator("✓ DEMOSTRACIÓN COMPLETADA")
        print("Todos los ejemplos se ejecutaron exitosamente.")
        print("\nPara más información, consulta el README.md")
        
    except Exception as e:
        logger.error("Error en la ejecución principal: %s", e)
        print(f"\n❌ Error: {e}")
        print("\nVerifica tu configuración en el archivo .env")
        raise


if __name__ == "__main__":
    main()
