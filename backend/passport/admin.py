from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline
from .models import Passport, Batch


@admin.register(Passport)
class PassportAdmin(UnfoldModelAdmin):
    list_display = (
        "full_name", 
        "status", 
        "batch",
        "published_at",
        "code", 
        "coupon_id", 
    )
    
    search_fields = (
        "code", 
        "coupon_id", 
        "first_name", 
        "last_name",
        "status",
    )

    list_filter = (
        "batch",
        "status", 
        "gender"
    )

    def full_name(self, obj):
        return f"{obj.last_name} {obj.middle_name} {obj.first_name}"
    full_name.short_description = _("Détenteur")


class PassportInline(TabularInline):
    model = Passport
    extra = 0
    show_change_link = True
    collapsible = True
    
    fields = [
        "code",
        "coupon_id",
        "last_name",
        "middle_name",
        "first_name",
        "gender",
        "status",
    ]


@admin.register(Batch)
class BatchAdmin(UnfoldModelAdmin):
    inlines = [PassportInline]
    
    # Champ "fantôme" en lecture seule
    readonly_fields = ["passports_placeholder"]

    list_display = ("id", "received_date", "status", "organization")
    list_filter = ("status", "organization")
    search_fields = ("id", "organization__name")

    fieldsets = (
        (
            _("Informations Générales"), 
            {
                "classes": ("tab",),
                "fields": (
                    "received_date",
                    "status",
                    "organization",
                ),
            },
        ),
        (
            _("Passeports"), # Titre de l'onglet
            {
                "classes": ("tab",),
                "fields": (
                    "passports_placeholder",
                ),
            },
        ),
    )

    def passports_placeholder(self, obj):
        # Gestion du cas "Ajout" (obj est None) vs "Modification"
        if not obj:
            return _("Veuillez d'abord sauvegarder le batch pour ajouter des passeports.")
        
        # Petit bonus : on compte les passeports pour donner une info utile
        count = obj.passport_set.count() if hasattr(obj, 'passport_set') else 0
        
        return format_html(
            """
            <div style="
                background-color: #eff6ff; 
                border-left: 4px solid #3b82f6; 
                padding: 16px; 
                border-radius: 4px; 
                color: #1e3a8a;">
                <h3 style="margin-top:0; font-weight:bold; font-size: 1.1em;">
                    Gestion des Passeports
                </h3>
                <p style="margin-bottom:0; font-size: 0.95em;">
                    Ce batch contient actuellement <strong>{}</strong> passeport(s).<br>
                    Le tableau de gestion détaillée se trouve <strong>ci-dessous</strong> &#8595;
                </p>
            </div>
            """,
            count
        )

    passports_placeholder.short_description = _("Info")

