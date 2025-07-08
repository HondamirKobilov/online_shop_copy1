from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProductViewSet, BasketViewSet, OrderViewSet,
    CategoryViewSet, SizeViewSet, ColorViewSet,
    ConnectUsViewSet, SocialMediaViewSet  # 🔹 Qo‘shildi
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'baskets', BasketViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'contact', ConnectUsViewSet)         # 🔹 Yangi qo‘shildi
router.register(r'social-media', SocialMediaViewSet)  # 🔹 Yangi qo‘shildi

urlpatterns = [
    path('', include(router.urls)),
]
