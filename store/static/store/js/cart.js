document.addEventListener('DOMContentLoaded', function() {
    // Utility function to display beautiful floating notifications (Toasts)
    function showToast(message) {
        // Use existing toast from base.html (id="cart-toast" / id="toast-message")
        const toast = document.getElementById('cart-toast');
        const msgSpan = document.getElementById('toast-message');
        if (!toast || !msgSpan) return;

        msgSpan.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // --- 1. Quick Add to Cart (Product Grid and Product Detail Pages) ---
    const addButtons = document.querySelectorAll('.add-to-cart-btn, #add-to-cart-detail');
    addButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            // Check if there is a quantity selector on the page
            const qtyInput = document.getElementById('quantity');
            const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Adding...`;

            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    quantity: quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update Cart badge in Navbar
                    const badge = document.getElementById('cart-count');
                    if (badge) {
                        badge.textContent = data.cart_total_count;
                        // Trigger CSS animation restart
                        badge.style.animation = 'none';
                        badge.offsetHeight; // Trigger reflow
                        badge.style.animation = null; 
                    }
                    showToast(data.message);
                } else {
                    showToast("Error adding product to cart.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast("Connection error. Try again.");
            })
            .finally(() => {
                button.disabled = false;
                button.innerHTML = originalText;
            });
        });
    });

    // --- 2. Shopping Cart Page Adjustments (Quantity & Removals) ---
    const cartWrapper = document.getElementById('cart-content-wrapper');
    if (cartWrapper) {
        // Quantity Adjustment: Minus Buttons
        const minusBtns = cartWrapper.querySelectorAll('.cart-minus-btn');
        minusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                const input = cartWrapper.querySelector(`.cart-qty-input[data-product-id="${productId}"]`);
                let val = parseInt(input.value);
                if (val > 1) {
                    updateCartQuantity(productId, val - 1, input);
                }
            });
        });

        // Quantity Adjustment: Plus Buttons
        const plusBtns = cartWrapper.querySelectorAll('.cart-plus-btn');
        plusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                const input = cartWrapper.querySelector(`.cart-qty-input[data-product-id="${productId}"]`);
                const max = parseInt(input.getAttribute('max'));
                let val = parseInt(input.value);
                if (val < max) {
                    updateCartQuantity(productId, val + 1, input);
                }
            });
        });

        // Remove Item Buttons
        const removeBtns = cartWrapper.querySelectorAll('.cart-remove-btn');
        removeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                removeCartItem(productId);
            });
        });
    }

    // Helper to send AJAX requests to update cart quantities
    function updateCartQuantity(productId, newQty, inputElement) {
        fetch(`/cart/update/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                quantity: newQty
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update input text
                inputElement.value = newQty;
                
                // Update item subtotal
                const itemSubtotal = document.getElementById(`subtotal-${productId}`);
                if (itemSubtotal) {
                    itemSubtotal.textContent = `\u20B9${Math.round(data.item_total_price)}`;
                }
                
                // Update Navbar count & Summary panels
                updatePageTotals(data.cart_total_count, data.cart_total_price);
            } else {
                showToast("Failed to update cart quantity.");
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showToast("Connection error.");
        });
    }

    // Helper to send AJAX requests to remove cart items
    function removeCartItem(productId) {
        const cartItemEl = document.getElementById(`cart-item-${productId}`);
        if (!cartItemEl) return;

        // Apply deletion animation
        cartItemEl.style.opacity = '0.5';

        fetch(`/cart/remove/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Fade out and remove from DOM
                cartItemEl.style.transition = 'all 0.3s ease';
                cartItemEl.style.opacity = '0';
                cartItemEl.style.transform = 'translateX(-30px)';
                
                setTimeout(() => {
                    cartItemEl.remove();
                    
                    // If cart is now completely empty, show empty message
                    if (data.cart_total_count === 0) {
                        const wrapper = document.getElementById('cart-content-wrapper');
                        const placeholder = document.getElementById('empty-cart-placeholder');
                        if (wrapper && placeholder) {
                            wrapper.innerHTML = placeholder.innerHTML;
                            wrapper.className = 'empty-cart-view';
                        }
                    }
                }, 300);

                // Update totals
                updatePageTotals(data.cart_total_count, data.cart_total_price);
                showToast(data.message);
            } else {
                cartItemEl.style.opacity = '1';
                showToast("Failed to remove item.");
            }
        })
        .catch(err => {
            cartItemEl.style.opacity = '1';
            console.error('Error:', err);
            showToast("Connection error.");
        });
    }

    // Update global navbar badge and cart summary fields
    function updatePageTotals(totalCount, totalCost) {
        const badge = document.getElementById('cart-count');
        if (badge) {
            badge.textContent = totalCount;
        }

        const summarySubtotal = document.getElementById('cart-summary-subtotal');
        const summaryTotal = document.getElementById('cart-summary-total');
        if (summarySubtotal && summaryTotal) {
            summarySubtotal.textContent = `\u20B9${Math.round(totalCost)}`;
            summaryTotal.textContent = `\u20B9${Math.round(totalCost)}`;
        }
    }
});
