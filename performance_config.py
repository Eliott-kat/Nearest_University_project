# Configuration optimisée pour performance
import logging

# Réduire le niveau de logging en production
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Configuration cache simple
PERFORMANCE_CONFIG = {
    'MONITORING_INTERVAL': 3,
    'CHUNK_SIZE': 50,
    'MAX_SOURCES': 10,
    'CACHE_TIMEOUT': 3600
}
