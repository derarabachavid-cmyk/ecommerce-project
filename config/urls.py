from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from store.views import (
    home,
    product_list,
    category_products,
    product_detail,
    add_to_cart,
    cart,
    update_cart,
    remove_from_cart,
    checkout,
    login_view,
    register_view,
    logout_view,
    my_orders,
    order_detail,
)

urlpatterns = [
    # HOME
    path("", home, name="home"),

    # PRODUCTS
    path("products/", product_list, name="product_list"),

    # CATEGORY
    path(
        "category/<int:pk>/",
        category_products,
        name="category_products",
    ),

    # PRODUCT DETAIL
    path(
        "products/<int:pk>/",
        product_detail,
        name="product_detail",
    ),

    # CART
    path("cart/", cart, name="cart"),
    path(
        "cart/add/<int:pk>/",
        add_to_cart,
        name="add_to_cart",
    ),
    path(
        "cart/update/<int:pk>/",
        update_cart,
        name="update_cart",
    ),
    path(
        "cart/remove/<int:pk>/",
        remove_from_cart,
        name="remove_from_cart",
    ),

    # CHECKOUT
    path("checkout/", checkout, name="checkout"),

    # AUTHENTICATION
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),

    # ORDERS
    path("orders/", my_orders, name="my_orders"),
    path(
        "orders/<int:pk>/",
        order_detail,
        name="order_detail",
    ),

    # ADMIN
    path("admin/", admin.site.urls),

    # API
    path("api/", include("store.urls")),
]

# MEDIA FILES
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)