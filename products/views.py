from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from .models import Category, Product, Order, OrderItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    OrderSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(
        username=username,
        email=email or "",
        password=password,
    )

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Registration successful.",
            "token": token.key,
            "username": user.username,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        username=username,
        password=password,
    )

    if user is None:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Login successful.",
            "token": token.key,
            "username": user.username,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    items = request.data.get("items", [])

    if not items:
        return Response(
            {"error": "Your cart is empty."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    total_price = 0
    order_items = []

    for item in items:
        product_id = item.get("product_id")
        quantity = int(item.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": f"Product {product_id} does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if product.stock < quantity:
            return Response(
                {"error": f"Not enough stock for {product.name}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_price += product.price * quantity

        order_items.append(
            {
                "product": product,
                "quantity": quantity,
                "price": product.price,
            }
        )

    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
    )

    for item in order_items:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            price=item["price"],
        )

        item["product"].stock -= item["quantity"]
        item["product"].save()

    return Response(
        {
            "message": "Order created successfully.",
            "order_id": order.id,
            "total_price": str(order.total_price),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)
