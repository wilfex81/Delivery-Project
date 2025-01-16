from django.contrib import admin
from .models import (
    Cart, CartItem,
    Product, Order,
    OrderItem, Address
    )

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)

