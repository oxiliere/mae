from django.contrib import admin
from .models import Passport, Batch
from unfold.admin import ModelAdmin as UnforldModelAdmin


@admin.register(Passport)
class PassportAdmin(UnforldModelAdmin):
    list_display = ("id", "code", "full_name", "status", "published_at")
    search_fields = ("code", "coupon_id", "first_name", "last_name")
    list_filter = ("status", "gender")

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Holder"



@admin.register(Batch)
class BatchAdmin(UnforldModelAdmin):
    title = "Test"
    list_display = ("id", "received_date", "status", "organization")
    list_filter = ("status", "organization")
    search_fields = ("id", "organization__name")

