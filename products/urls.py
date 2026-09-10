from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    CategoryViewSet,
    OrderCreateView,
    MyOrdersView,
    RegisterView,
)


router = DefaultRouter()

router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")


urlpatterns = router.urls + [
    path(
        "orders/",
        OrderCreateView.as_view(),
        name="create-order",
    ),

    path(
        "my-orders/",
        MyOrdersView.as_view(),
        name="my-orders",
    ),

    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
]