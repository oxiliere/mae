
# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

from .base import BASE_DIR

LANGUAGE_CODE = "fr-FR"

USE_I18N = True

USE_L10N = True

TIME_ZONE = "Africa/Lubumbashi"

USE_TZ = True

LOCALE_PATHS = [ BASE_DIR / "locale" ]