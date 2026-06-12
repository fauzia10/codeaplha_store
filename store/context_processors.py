from .cart import Cart

def cart_items_count(request):
    """
    Context processor to return the cart object and global total count to all templates.
    """
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_total_count': len(cart)
    }
