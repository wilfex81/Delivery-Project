from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    
    path('orders/', views.OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    
    path('cart/', views.Cart.as_view(), name='cart-view'),
    path('cart-item/update/<int:cart_item_id>/', views.CartItemUpdate.as_view(), name='cart-item-update'),
    path('cart-item/delete/<int:cart_item_id>/', views.CartItemDelete.as_view(), name='cart-item-delete'),
]
