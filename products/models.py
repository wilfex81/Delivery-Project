from django.db import models

from users.models import User

class Product(models.Model):
    """
    Represent product the seller(admin) uploads
    """
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    
class Order(models.Model):
    """
    Track customer orders, linking clients to the products purchased
    """
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem')
    total_prices = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='pending')
    
    def __str__(self):
        return f"Order #{self.id} by {self.client.username}"
    

class OrderItem(models.Model):
    """
    Represents each product in an order, including quantity and price at the time of the order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    

class Address(models.Model):
    """
    Handles delivery addresses
    """
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)# at some point provide a list of counties buddy
    country = models.CharField(max_length=100)# at some ponit provide a list of counntries buddy

    def __str__(self):
        return f"{self.street}, {self.city}, {self.county}, {self.country}"
    
class Cart(models.Model):
    """
    Add product(s) to cart before placing an order
    """
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    products = models.ManyToManyField(Product, through= 'CartItem')
    
    def __str__(self):
        return f"Cart for {self.client.username}"
    
class CartItem(models.Model):
    """
    Represent products in a cart with quantity
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
