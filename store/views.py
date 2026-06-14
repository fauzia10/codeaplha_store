from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from .models import Product
from .cart import Cart
from .mongo_auth import register_user, authenticate_user, get_user_by_id
import json


# ─────────────────────────────────────────────
#  MongoDB Auth Views
# ─────────────────────────────────────────────

def register_view(request):
    """Show register form (GET) or create a new MongoDB user (POST)."""
    if request.session.get('mongo_user_id'):
        return redirect('store:product_list')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
        elif password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            result = register_user(username, email, password)
            if result['success']:
                messages.success(request, 'Account created! Please log in.')
                return redirect('store:login')
            else:
                messages.error(request, result['error'])

    return render(request, 'store/register.html')


def login_view(request):
    """Show login form (GET) or authenticate against MongoDB (POST)."""
    if request.session.get('mongo_user_id'):
        return redirect('store:product_list')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
        else:
            user = authenticate_user(username, password)
            if user:
                request.session['mongo_user_id']   = user['_id']
                request.session['mongo_username']  = user['username']
                request.session['mongo_email']     = user.get('email', '')
                messages.success(request, f"Welcome back, {user['username']}!")
                return redirect('store:product_list')
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'store/login.html')


def logout_view(request):
    """Clear the MongoDB session and redirect to login."""
    request.session.flush()
    messages.info(request, 'You have been logged out.')
    return redirect('store:login')


def profile_view(request):
    """Show logged-in user profile."""
    user_id = request.session.get('mongo_user_id')
    if not user_id:
        return redirect('store:login')
    user = get_user_by_id(user_id)
    return render(request, 'store/profile.html', {'mongo_user': user})

def product_list(request):
    """
    List all products, with optional search and category filtering.
    All products are sent to the template; category filtering is handled
    client-side via JS for instant no-reload UX.
    """
    query = request.GET.get('q', '')
    if query:
        products = (
            Product.objects.filter(name__icontains=query) |
            Product.objects.filter(description__icontains=query)
        )
    else:
        products = Product.objects.all()

    # Distinct ordered category list for the filter bar
    categories = list(Product.objects.values_list('category', flat=True).distinct().order_by('category'))

    context = {
        'products':   products,
        'query':      query,
        'categories': categories,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    """
    Display details of a single product.
    """
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)

@ensure_csrf_cookie
def cart_detail(request):
    """
    Display the contents of the shopping cart.
    """
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    """
    AJAX view to add a product to the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        override = data.get('override', False)
    except (json.JSONDecodeError, ValueError):
        quantity = 1
        override = False

    cart.add(product=product, quantity=quantity, override_quantity=override)
    
    return JsonResponse({
        'success': True,
        'cart_total_count': len(cart),
        'message': f"Added '{product.name}' to cart!"
    })

@require_POST
def cart_remove(request, product_id):
    """
    AJAX view to remove a product from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    return JsonResponse({
        'success': True,
        'cart_total_count': len(cart),
        'cart_total_price': float(cart.get_total_price()),
        'message': f"Removed '{product.name}' from cart!"
    })

@require_POST
def cart_update(request, product_id):
    """
    AJAX view to update product quantity in the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)

    # Perform updates
    cart.add(product=product, quantity=quantity, override_quantity=True)
    
    # Calculate item's new total price
    item_total_price = 0.00
    for item in cart:
        if item['product'].id == product.id:
            item_total_price = float(item['total_price'])
            break

    return JsonResponse({
        'success': True,
        'item_total_price': item_total_price,
        'cart_total_count': len(cart),
        'cart_total_price': float(cart.get_total_price()),
    })
