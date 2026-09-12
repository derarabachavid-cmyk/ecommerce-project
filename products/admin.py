from django.contrib import admin

from .models import (
    Category,
    Product,
    Order,
    OrderItem,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
    ]

    search_fields = [
        "name",
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
        "price",
        "stock",
        "category",
    ]

    list_filter = [
        "category",
    ]

    search_fields = [
        "name",
        "description",
    ]


class OrderItemInline(
    admin.TabularInline
):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user",
        "total_price",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
        "created_at",
    ]

    search_fields = [
        "user__username",
    ]

    inlines = [
        OrderItemInline
    ]