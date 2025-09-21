# Configuration de performance pour l'application TCA
# Ce fichier contient les paramètres d'optimisation

# Pagination
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100

# Cache
CACHE_TTL = 300  # 5 minutes

# Base de données
DB_OPTIMIZATION = True
DB_INDEXES = True

# Templates
TEMPLATE_MINIFICATION = True
CSS_MINIFICATION = True
JS_MINIFICATION = True

# Performance
ENABLE_CACHE = True
ENABLE_COMPRESSION = True
ENABLE_INDEXING = True
