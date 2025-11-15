import os



REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/1")

CACHEOPS_REDIS = REDIS_URL


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CACHEOPS_DEFAULTS = {
    'timeout': 60*60
}

CACHEOPS = {
    'organisations.*': {'ops': 'all', 'timeout': 60*25},
    'users.User': {'ops': 'all', 'timeout': 60*30},
}

