from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import (
    Order, Cart, 
    CartItem, Product
    )
from .serializers import (
    OrderSerializer,
    ProductSerializer,
    CartSerializer, 
    CartItemSerializer
    )

class ProductList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Returns a list of products with their details.

        HTTP Method: Get
        """
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Create a new product.

        The seller will be automatically associated with the product. 
        Requires the product details to be sent in the request body.

        HTTP Method: POST
        """   
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProductDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(Self, request, pk):
        """
        Retrieve the details of a specific product.
        
        The product is identified by the `pk` 
        (primary key) provided in the URL.

        HTTP Method: GET
        """  
        
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """
        Update the details of a specific product.

        Sellers (users) who own the product can update it. 
        The product is identified
        by the `pk` (primary key) provided in the URL.

        HTTP Method: PUT
        """  
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete a specific product.

        Sellers (users) who own the product can delete it.
        The product is identified 
        by the `pk` (primary key) provided in the URL.

        HTTP Method: DELETE
        """  
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OrderList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retrieve a list of orders placed a user

        The list of orders is filtered to include 
        only the orders placed by the currently authenticated user.

        HTTP Method: GET
        """   
        orders = Order.objects.filter(client = request.user)
        serializer = OrderSerializer(orders, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Create a new order.

        The order details must be provided in 
        the request body, including the list of products the user wants to order.

        HTTP Method: POST
        """
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderDetail(APIView):
    permission_classes = [IsAuthenticated]  # JWT protection

    def get(self, request, pk):
        """
        Retrieve the details of a specific order.

        Users who are the owner (client) of the order can access this view. 
        The order is identified by the `pk` (primary key) provided in the URL.

        HTTP Method: GET
        """
        try:
            order = Order.objects.get(pk=pk, client=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update the details of a specific order.

        Client who placed the order can update the order. The order is identified 
        by the `pk` (primary key) provided in the URL.

        HTTP Method: PUT
        """
        try:
            order = Order.objects.get(pk=pk, client=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a specific order.

        Users who are the owner (client) of the order can delete it. The order is identified 
        by the `pk` (primary key) provided in the URL.

        HTTP Method: DELETE
        """
        try:
            order = Order.objects.get(pk=pk, client=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class Cart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the cart of the user(client).
        
        including the products added to the cart and their quantities.

        HTTP Method: GET
        """
        cart, created = Cart.objects.get_or_create(client=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """
        Add a product to the cart
        with a specified quantity. 
        If the product already exists in the cart, it will update the quantity.

        HTTP Method: POST
        """
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id or not quantity:
            return Response({"detail": "Product ID and quantity are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        cart, created = Cart.objects.get_or_create(client=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        cart_item.quantity += quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, cart_item_id):
        """
        Update the quantity of a cart item.

        This will update the quantity of a specific product in the user's cart. 
        The `cart_item_id` is used to identify the cart item to update.

        HTTP Method: PUT
        """
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__client=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        if quantity is None or quantity <= 0:
            return Response({"detail": "Quantity must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

class CartItemDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_item_id):
        """
        Delete a specific product from the cart.

        This will remove a specific product from the user's cart. The `cart_item_id` 
        is used to identify the cart item to delete.

        HTTP Method: DELETE
        """
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__client=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)