"""App configuration for shop_admin app."""
from django.apps import AppConfig


class ShopAdminConfig(AppConfig):
    """Configuration for the shop_admin app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shop_admin"
    verbose_name = "Shop Admin Panel"
