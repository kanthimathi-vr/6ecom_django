# store/utils.py
import json
from django.core.exceptions import ObjectDoesNotExist
# Assuming these are your models
from .models import Product, Order, OrderItem, Customer 

def cookie_cart(request):
    """
    Handles fetching cart data for an anonymous (guest) user from browser cookies.
    """
    try:
        # Load the cart cookie, which is stored as a JSON string
        cart = json.loads(request.COOKIES['cart'])
    except:
        # If cookie doesn't exist or is invalid, initialize an empty cart
        cart = {}
    
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cart_items_count = order['get_cart_items']

    # Note: cart.items() returns (product_id_string, quantity)
    for product_id, quantity in cart.items():
        try:
            # The cookie stores product IDs as strings, so convert back to int
            product = Product.objects.get(id=int(product_id)) 
            
            # Calculate item total
            total = (product.price * quantity)
            
            # Update order totals
            order['get_cart_total'] += total
            order['get_cart_items'] += quantity
            cart_items_count = order['get_cart_items']
            
            # Check if shipping is required
            if product.digital == False:
                order['shipping'] = True

            # Structure the item data
            item = {
                'product': product,
                'quantity': quantity,
                'get_total': total,
                'product_id': product.id,
            }
            items.append(item)
            
        except Product.DoesNotExist:
            print(f"DEBUG: Product ID {product_id} is in cookie but NOT in database!")
            
            # Optionally log this, but passing is common for guest carts
            pass
            
    return {'cart_items_count': cart_items_count, 'order': order, 'items': items, 'customer': None} # Added customer: None for consistency


def cart_data(request):
    """
    Determines the user type and returns the correct cart data structure.
    
    FIX: Uses try/except to handle cases where a logged-in User has no 
    associated Customer profile, preventing RelatedObjectDoesNotExist.
    """
    if request.user.is_authenticated:
        # LOGGED-IN USER: Get cart data from the database
        user = request.user
        
        try:
            # Attempt to retrieve the customer profile
            customer = user.customer 
            
        except ObjectDoesNotExist:
            # If the customer profile is missing, create it automatically.
            # IMPORTANT: Ensure the fields (user, name, email) match your Customer model
            customer = Customer.objects.create(
                user=user, 
                name=user.username,
                email=user.email
            )

        # Proceed with fetching or creating the Order, now that 'customer' is guaranteed to exist
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items_count = order.get_cart_items
        
    else:
        # GUEST USER: Get cart data from cookies
        cookie_data = cookie_cart(request)
        cart_items_count = cookie_data['cart_items_count']
        order = cookie_data['order']
        items = cookie_data['items']
        customer = cookie_data['customer'] # Will be None from cookie_cart
        
    return {'cart_items_count': cart_items_count, 'order': order, 'items': items, 'customer': customer}
