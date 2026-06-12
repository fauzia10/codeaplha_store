from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Product
from .cart import Cart
import json

def product_list(request):
    """
    List all products, with optional search filtering.
    """
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query) | Product.objects.filter(description__icontains=query)
    else:
        products = Product.objects.all()
    
    context = {
        'products': products,
        'query': query
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
