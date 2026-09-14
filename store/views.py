from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, CheckoutForm
from .models import Category, Product, Order, OrderItem


# =========================================================
# CART
# =========================================================

def get_cart(request):
    return request.session.get("cart", {})


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def get_cart_items(request):
    cart = get_cart(request)

    items = []
    total = Decimal("0.00")
    cart_count = 0

    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()

        if not product:
            continue

        quantity = int(quantity)
        subtotal = product.price * quantity

        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

        total += subtotal
        cart_count += quantity

    return items, total, cart_count


# =========================================================
# HOME
# =========================================================

def home(request):
    products = Product.objects.all().order_by("-created_at")
    categories = Category.objects.all()

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "home.html",
        {
            "featured_products": products,
            "latest_products": products,
            "categories": categories,
            "cart_count": cart_count,
        },
    )


# =========================================================
# PRODUCTS
# =========================================================

def product_list(request):
    products = Product.objects.all().order_by("-created_at")

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "products.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
            "selected_category": category_id,
            "cart_count": cart_count,
        },
    )


def category_products(request, pk):
    category = get_object_or_404(Category, pk=pk)

    products = Product.objects.filter(
        category=category
    ).order_by("-created_at")

    categories = Category.objects.all()

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "products.html",
        {
            "products": products,
            "categories": categories,
            "category": category,
            "cart_count": cart_count,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    )[:4]

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "related_products": related_products,
            "cart_count": cart_count,
        },
    )


# =========================================================
# CART ACTIONS
# =========================================================

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.stock <= 0:
        messages.error(
            request,
            "This product is currently out of stock."
        )
        return redirect("product_detail", pk=product.pk)

    cart = get_cart(request)
    product_id = str(product.id)

    current_quantity = int(
        cart.get(product_id, 0)
    )

    if current_quantity >= product.stock:
        messages.warning(
            request,
            "You cannot add more than the available stock."
        )
        return redirect("cart")

    cart[product_id] = current_quantity + 1

    save_cart(request, cart)

    messages.success(
        request,
        f"{product.name} was added to your cart."
    )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "product_list"
        )
    )


def cart(request):
    items, total, cart_count = get_cart_items(request)

    return render(
        request,
        "cart.html",
        {
            "items": items,
            "total": total,
            "cart_count": cart_count,
        },
    )


def update_cart(request, pk):
    if request.method != "POST":
        return redirect("cart")

    product = get_object_or_404(Product, pk=pk)

    try:
        quantity = int(
            request.POST.get("quantity", 1)
        )
    except ValueError:
        quantity = 1

    cart = get_cart(request)
    product_id = str(product.id)

    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        quantity = min(quantity, product.stock)
        cart[product_id] = quantity

    save_cart(request, cart)

    return redirect("cart")


def remove_from_cart(request, pk):
    cart = get_cart(request)

    cart.pop(str(pk), None)

    save_cart(request, cart)

    messages.success(
        request,
        "Product removed from your cart."
    )

    return redirect("cart")


# =========================================================
# REGISTER
# =========================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                "Account created successfully!"
            )

            return redirect("home")
    else:
        form = RegisterForm()

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "register.html",
        {
            "form": form,
            "cart_count": cart_count,
        },
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()

            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            return redirect(
                request.GET.get(
                    "next",
                    "home"
                )
            )
    else:
        form = AuthenticationForm()

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "login.html",
        {
            "form": form,
            "cart_count": cart_count,
        },
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):
    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("home")


# =========================================================
# CHECKOUT
# =========================================================

@login_required(login_url="login")
def checkout(request):

    items, total, cart_count = get_cart_items(request)

    if not items:
        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("product_list")

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                # Check stock before creating order
                for item in items:

                    product = Product.objects.select_for_update().get(
                        id=item["product"].id
                    )

                    if product.stock < item["quantity"]:

                        messages.error(
                            request,
                            f"Not enough stock for {product.name}."
                        )

                        return redirect("cart")

                # Create order WITH delivery information
                order = Order.objects.create(
                    user=request.user,

                    full_name=form.cleaned_data["full_name"],

                    email=form.cleaned_data["email"],

                    address=form.cleaned_data["address"],

                    city=form.cleaned_data["city"],

                    total_price=total,

                    status="Pending",
                )

                # Create order items
                for item in items:

                    product = Product.objects.get(
                        id=item["product"].id
                    )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item["quantity"],
                        price=product.price,
                    )

                    product.stock -= item["quantity"]

                    product.save(
                        update_fields=["stock"]
                    )

                # Empty cart
                request.session["cart"] = {}

                request.session.modified = True

            messages.success(
                request,
                "Your order has been placed successfully!"
            )

            return redirect(
                "order_detail",
                pk=order.pk
            )

    else:

        form = CheckoutForm(
            initial={
                "full_name": request.user.get_full_name(),
                "email": request.user.email,
            }
        )

    return render(
        request,
        "checkout.html",
        {
            "items": items,
            "total": total,
            "cart_count": cart_count,
            "form": form,
        },
    )

# =========================================================
# MY ORDERS
# =========================================================

@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "orders.html",
        {
            "orders": orders,
            "cart_count": cart_count,
        },
    )


# =========================================================
# ORDER DETAIL
# =========================================================

@login_required(login_url="login")
def order_detail(request, pk):
    order = get_object_or_404(
        Order,
        pk=pk,
        user=request.user
    )

    _, _, cart_count = get_cart_items(request)

    return render(
        request,
        "order_detail.html",
        {
            "order": order,
            "cart_count": cart_count,
        },
    )