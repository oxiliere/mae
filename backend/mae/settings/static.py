# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
from .base import BASE_DIR


STATIC_URL = "/static/"


STATICFILES_DIRS = [
    BASE_DIR / "static",
]

