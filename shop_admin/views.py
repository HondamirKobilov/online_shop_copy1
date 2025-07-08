from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import User, Product, Basket, Order, Category, Size, Color, ConnectUs, SocialMedia
from .serializers import (
    UserSerializer, ProductSerializer, BasketSerializer, OrderSerializer,
     CategorySerializer, SizeSerializer, ColorSerializer, ConnectUsSerializer, SocialMediaSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class BasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"DELETE log: Basket #{instance.id}")  # log chiqadi
        return super().destroy(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class ConnectUsViewSet(viewsets.ModelViewSet):
    queryset = ConnectUs.objects.all()
    serializer_class = ConnectUsSerializer

class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
