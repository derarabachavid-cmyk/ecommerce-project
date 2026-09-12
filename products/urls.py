from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    CategoryViewSet,
    register,
    login,
    create_order,
    my_orders,
)

router = DefaultRouter()

router.register(
    "products",
    ProductViewSet,
    basename="product",
)

router.register(
    "categories",
    CategoryViewSet,
    basename="category",
)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("orders/create/", create_order, name="create-order"),
    path("orders/", my_orders, name="my-orders"),
]
