from rest_framework import serializers
from .models import(
    Product, Order,
    OrderItem,CartItem,
    Cart,
    )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'seller', 'name', 'description', 'price', 'stock_quantity', 'image', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_time_of_order']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'products', 'total_price', 'order_date', 'status']
        
    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        
        for item_data in products_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True)

    class Meta:
        model = Cart
        fields = ['id', 'client', 'items', 'created_at', 'updated_at']
