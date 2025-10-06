# store/context_processors.py
import json
from .models import Order, Customer # Make sure to import Customer!
from django.core.exceptions import ObjectDoesNotExist

def cart_context(request):
    """
    A context processor to make cart_items_count available globally in all templates.
    FIXED: Safely retrieves the Customer object before querying the Order model.
    """
    cart_items_count = 0

    if request.user.is_authenticated:
        user = request.user
        
        # 1. SAFELY GET OR CREATE THE CUSTOMER PROFILE
        try:
            # Try to get the Customer object linked to the User
            customer = user.customer 
            
        except ObjectDoesNotExist:
            # If it doesn't exist (e.g., brand new user), create it.
            customer = Customer.objects.create(
                user=user, 
                name=user.username,
                email=user.email
            )

        # 2. USE THE CUSTOMER OBJECT to get the Order (THIS WAS THE FAULTY LINE)
        # We also use get_or_create defensively here.
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
        # 3. Get the cart item count
        cart_items_count = order.get_cart_items
        
    else:
        # GUEST USER: Get item count from the cookie (simplified version)
        try:
            cart = json.loads(request.COOKIES.get('cart', '{}'))
        except json.JSONDecodeError:
            cart = {}
            
        for product_id, item_data in cart.items():
            # item_data might be a quantity or a dict with quantity; assuming quantity
            if isinstance(item_data, int):
                cart_items_count += item_data
            elif isinstance(item_data, dict) and 'quantity' in item_data:
                 cart_items_count += item_data['quantity']

    return {'cart_items_count': cart_items_count}