"""
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _



UNFOLD = {

    "SITE_URL": "/",
    "SITE_ICON": lambda request: static("branding/icon.svg"),  # both modes, optimise for 32px height
    "SITE_LOGO": lambda request: static("branding/logo.svg"),  # both modes, optimise for 32px height
    "SITE_SYMBOL": "speed",                                    # symbol from icon set
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("branding/favicon.svg"),
        },
    ],
    "SHOW_HISTORY": True,           # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True,      # show/hide "View on site" button, default: True
    "SHOW_BACK_BUTTON": True,       # show/hide "Back" button on changeform in header, default: False



    "BORDER_RADIUS": "6px",
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
            },
        },
    },
    "SIDEBAR": {
        "show_title": True,

    },
}

"""