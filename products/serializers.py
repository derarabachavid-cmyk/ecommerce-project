from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Product, Category, Order, OrderItem


# ============================================================
# CATEGORY SERIALIZER
# ============================================================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
        ]


# ============================================================
# PRODUCT SERIALIZER
# ============================================================

class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_name",
            "price",
            "stock",
            "image",
            "created_at",
        ]


# ============================================================
# ORDER ITEM SERIALIZER
# ============================================================

class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price",
        ]

        read_only_fields = [
            "id",
            "product_name",
            "price",
        ]


# ============================================================
# ORDER SERIALIZER
# ============================================================

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "user",
            "name",
            "email",
            "address",
            "city",
            "items",
            "total",
            "total_price",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "total",
            "total_price",
            "created_at",
        ]

    # --------------------------------------------------------
    # Calculate total price
    # --------------------------------------------------------

    def get_total_price(self, order):

        total = 0

        for item in order.items.all():
            total += item.price * item.quantity

        return total

    # --------------------------------------------------------
    # Create order + order items
    # --------------------------------------------------------

    def create(self, validated_data):

        items_data = validated_data.pop("items")

        # Calculate total from actual product prices
        total = 0

        for item_data in items_data:

            product = item_data["product"]
            quantity = item_data["quantity"]

            # Check stock
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}."
                )

            total += product.price * quantity

        # Create the order
        order = Order.objects.create(
            total=total,
            **validated_data
        )

        # Create order items
        for item_data in items_data:

            product = item_data["product"]
            quantity = item_data["quantity"]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )

            # Reduce product stock
            product.stock -= quantity
            product.save()

        return order


# ============================================================
# REGISTER SERIALIZER
# ============================================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "password",
        ]

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )

        return user