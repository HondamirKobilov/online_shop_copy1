from rest_framework import serializers
from .models import (
    User, Product, Basket, Order, OrderDetail,
    Category, Size, Color, ConnectUs, SocialMedia
)


# 👤 Foydalanuvchi serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


# 🏷️ Kategoriya, o'lcham, rang
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']


# 📦 Mahsulot serializer
class ProductSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True, read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'



# 🧺 Savat (Basket) serializer
class BasketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    color = ColorSerializer(read_only=True)
    color_id = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), source='color', write_only=True, allow_null=True, required=False
    )

    size = SizeSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), source='size', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Basket
        fields = [
            'id', 'number',
            'user', 'user_id',
            'product', 'product_id',
            'color', 'color_id',
            'size', 'size_id'
        ]
# shows human-readable color name

from rest_framework import serializers
from .models import Order, OrderDetail

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['product', 'number', 'color', 'size']  # 🔧 size qo‘shildi


class OrderSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'phone', 'status', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        order = Order.objects.create(**validated_data)
        for detail in details_data:
            OrderDetail.objects.create(order=order, **detail)
        return order


class ConnectUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectUs
        fields = '__all__'

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = '__all__'