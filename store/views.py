# store/views.py

import json
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal
# Import all necessary models
from .models import Product, Order, OrderItem, Category, Customer # Assuming Customer is imported here
from .utils import cart_data 


# Initialize Razorpay client (Keep this at the module level)
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def home(request, category_slug=None):
    
    # 1. Get ALL necessary data from the utility function.
    data = cart_data(request)
    customer = data['customer']
    cart_items_count = data['cart_items_count']
    
    # Existing product/category logic
    try:
        products = Product.objects.all()
        categories = Category.objects.all()
    except Exception: # Use a general catch for model import/DB errors during development
        products = []
        categories = []
    
    selected_category_slug = None
    if category_slug:
        selected_category_slug = category_slug
        # Filter the queryset if a category slug is provided
        products = products.filter(category__slug=category_slug)
    
    # Products for Carousel (e.g., first 3 products)
    carousel_products = products[:3]
    
    # Products for Suggested/Featured Section (e.g., last 4 products)
    suggested_products = Product.objects.order_by('-id')[:4]
    
    # Product Features (static data)
    features = [
        {"icon": "bi-lightning-charge", "title": "Fast Delivery", "description": "Get your order in 3-5 business days."},
        {"icon": "bi-shield-check", "title": "Secure Payments", "description": "100% secure payment gateway with SSL."},
        {"icon": "bi-arrow-repeat", "title": "Easy Returns", "description": "30-day no-hassle return policy."},
    ]
    
    # IMPORTANT: Removed ALL TeamMember/Testimonial queries from 'home' view
    # to eliminate the likely source of the persistent ValueError.
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category_slug': selected_category_slug,
        'carousel_products': carousel_products,
        'suggested_products': suggested_products,
        'features': features,
        # 'team_members': team_members, # Removed
        # 'testimonials': testimonials, # Removed
        
        # Data sourced from the cart_data utility
        'customer': customer,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'store/index.html', context)


# --- ABOUT US VIEW ---
def about(request):
    # CRITICAL FIX/AVOIDANCE: Temporarily removing the DB query to isolate the ValueError.
    # If the TeamMember model is the source of the persistent error, this prevents the query.
    # If you want to use TeamMember, you MUST fix its model definition/properties.
    team_members = [] # Assuming TeamMember model/query was problematic
    
    context = {
        'team_members': team_members
    }
    return render(request, 'store/about.html', context)


# --- CONTACT US VIEW ---
def contact(request):
    return render(request, 'store/contact.html')


# store/views.py

def cart_view(request):
    # Assuming you have a function/utility to get cart data
    # (This is often where the guest/authenticated logic lives)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        # Ensure 'complete=False' correctly fetches the current active cart
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all() # Fetching all items related to the order
    else:
        # Handle cookie/guest session data (often results in an empty or dummy order/items)
        order = {'get_cart_total': 0, 'get_cart_items': 0} # Dummy data if needed
        items = []

    context = {
        'items': items,
        'order': order,  # <--- THIS MUST BE THE ORDER OBJECT
        # 'cart_items_count': order.get_cart_items # Optional
    }
    return render(request, 'store/cart.html', context)



from django.shortcuts import render, redirect # Ensure 'redirect' is imported
from .models import Order, Customer, ShippingAddress # Ensure ShippingAddress is imported



def checkout_view(request):
    # This logic should mirror the part of cart_view that fetches the order

    if request.user.is_authenticated:
        customer = request.user.customer
        # 1. Fetch the active Order object
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        # Redirect guests to login/cart if guest checkout is not implemented
        return redirect('store:login') # Or 'store:cart' with an error message

    
    if request.method == 'POST':
    # 1. Get data from the form (VERIFY THESE NAMES MATCH checkout.html)
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2') # Check if this name is correct
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        payment_method = request.POST.get('payment_method')
        
    # 2. VALIDATION: Check the required fields
        required_fields = [full_name, address_line_1, city, state, zipcode]
    
        if any(not field for field in required_fields):
            print("Missing required fields!") 
            # We print the message you saw, but we MUST redirect here.
            return redirect('store:checkout') # Rerender the page and force user to enter data

        # 3. Save the Shipping Address (Assuming a ShippingAddress model)
        # Note: You need to create or update a ShippingAddress instance here
        shipping_address, created = ShippingAddress.objects.update_or_create(
             customer=customer,
             defaults={
                 'name': full_name,
                 'email': email,
                 'address': address_line_1,
                 'city': city,
                 'state': state,
                 'zipcode': zipcode,
             }
        )
        
        # 4. Save the payment method choice to the session or the Order object
        request.session['payment_method'] = payment_method
        
        # 5. Redirect to the next step (payment initiation/review page)
        # We redirect to the payment view defined in your urls.py
        return redirect('store:initiate_payment')

    # --- GET REQUEST (Initial page load) ---
    else:
        # Add the Order object to the context
        context = {
            'items': items,
            'order': order,
            # Optional: Pass default address data if customer has saved one
            # 'default_address': ShippingAddress.objects.filter(customer=customer).first()
        }
        return render(request, 'store/checkout.html', context)
    
# --- NEW NAME FOR AJAX VIEW ---
def updateCartAjax(request):
    # ... KEEP ALL YOUR EXISTING LOGIC AS IS ...
    # This view still expects POST data via request.body
    # It does NOT accept product_id from the URL.
    pass

def updateCartPage(request, product_id):
    """
    Handles POST from the cart quantity form and GET from the 'Remove' link.
    """
    # 1. Get the necessary objects
    product = get_object_or_404(Product, id=product_id)
    
    # 2. Identify the customer (either authenticated or guest cookie logic)
    # This logic should be similar to what you use in your cart_data utility
    if request.user.is_authenticated:
        customer = request.user.customer
        # Get the open order for this customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        # Placeholder: If not logged in, you need to handle session/cookie logic here
        # For a GET request (like 'Remove'), this is complex. We focus on authenticated first.
        return redirect('store:cart') 

    # 3. Find the specific item in the order
    try:
        orderItem = OrderItem.objects.get(order=order, product=product)
    except OrderItem.DoesNotExist:
        # Item wasn't in the cart, just redirect
        return redirect('store:cart')

    # --- MAIN LOGIC ---
    
    if request.method == 'POST':
        # Handles the quantity update form (NOT the 'Remove' link)
        try:
            quantity = int(request.POST.get('quantity', 0))
        except ValueError:
            quantity = orderItem.quantity # Safety fallback
        
        if quantity > 0:
            orderItem.quantity = quantity
            orderItem.save()
        else:
            orderItem.delete()
            
    # The 'Remove' link is a GET request and runs this block
    else: 
        # Action for the removal link: simply delete the item
        orderItem.delete()
        
    return redirect('store:cart')

# --- PRODUCT DETAIL VIEW ---
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    suggested_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product_id).order_by('?')[:4]
    
    context = {
        'product': product,
        'suggested_products': suggested_products
    }
    return render(request, 'store/product_detail.html', context)


# --- USER AUTH VIEWS ---

def register_user(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:home') 
    else:
        form = UserCreationForm()
    
    return render(request, 'store/register.html', {'form': form}) 


def login_user(request):
    """Handles user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) 
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store:home')
    else:
        form = AuthenticationForm()
        
    return render(request, 'store/login.html', {'form': form})


def logout_user(request):
    """Logs the user out and redirects to the store home page."""
    logout(request)
    return redirect('store:home')


def add_to_cart(request, product_id):
    # This view is typically used to handle a redirect after adding an item
    return redirect('store:cart') 


# --- PAYMENT VIEWS (Razorpay) ---
# store/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Order, Customer, ShippingAddress
from django.conf import settings
from django.contrib import messages
import time # Used in finalize_cod_order
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse # Use HttpResponse for the response you showed
SHIPPING_FEE = Decimal('10.00')
# Ensure Razorpay/payment library is imported if needed
def get_current_order(request):
    if not request.user.is_authenticated:
        return None, None
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # Ensure the order has a linked shipping address for the confirmation page
    shipping_address = ShippingAddress.objects.filter(customer=customer).order_by('-date_added').first()
    return order, shipping_address


# --- 1. initiate_payment (Final Review Page) ---
def initiate_payment(request):
    """
    Renders the final review page before payment, confirming address and method.
    """
    order, shipping_address = get_current_order(request)
    
    if not order or not shipping_address:
         messages.error(request, "Order or shipping address is missing.")
         return redirect('store:checkout')

    payment_method = request.session.get('payment_method')

    # --- NEW CALCULATION ---
    # We assume order.get_cart_total is available on the Order model
    try:
        subtotal = order.get_cart_total
        grand_total = subtotal + SHIPPING_FEE
    except AttributeError:
        # Handle case where even get_cart_total is missing, though less likely
        grand_total = 0.00 
        subtotal = 0.00
        messages.error(request, "Error calculating order total.")
        return redirect('store:checkout')
    
    context = {
        'order': order,
        'shipping_address': shipping_address,
        'payment_method': payment_method,
    }
    return render(request, 'store/initiate_payment.html', context)


# --- 2. finalize_cod_order (COD Success Path) ---
def finalize_cod_order(request):
    """
    Finalizes the order for Cash on Delivery and redirects to the success page.
    """
    order, _ = get_current_order(request)
    
    if not order:
        messages.error(request, "Cannot finalize order: cart is empty.")
        return redirect('store:checkout')
        
    subtotal = order.get_cart_total
    grand_total = subtotal + SHIPPING_FEE # Use the global SHIPPING_FEE

    # Set status for COD
    order.complete = True
    order.transaction_id = f'COD-{order.id}-{int(time.time())}' # Simple unique ID
    order.payment_method = 'COD'
    order.status = 'Pending' # Or 'Processing'
    order.save()
    
    # Clean up the session payment method
    if 'payment_method' in request.session:
        del request.session['payment_method']
        
    # Redirect to the common success page
    return redirect('store:order_complete')


# --- 3. process_razorpay_payment (Razorpay Setup Path) ---
def process_razorpay_payment(request):
    """
    Creates the Razorpay Order and renders the payment gateway page to launch the modal.
    """
    order, shipping_address = get_current_order(request)
    
    if not order:
        messages.error(request, "Order not found.")
        return redirect('store:checkout')

    # Calculate total including shipping
    amount_due = order.get_total_with_shipping() # Assuming this method exists
    amount_in_paise = int(amount_due * 100) # Razorpay requires amount in smallest unit

    # --- RAZORPAY API CALL (MOCK/EXAMPLE) ---
    # This requires the actual Razorpay client setup and API keys
    # try:
    #     razorpay_order = RAZORPAY_CLIENT.order.create({
    #         'amount': amount_in_paise, 
    #         'currency': 'INR',
    #         'payment_capture': '1'
    #     })
    #     order.razorpay_order_id = razorpay_order['id']
    #     order.save()
    # except Exception as e:
    #     messages.error(request, f"Payment setup failed: {e}")
    #     return redirect('store:checkout')

    # --- MOCK RAZORPAY DATA FOR DESIGN TESTING ---
    mock_razorpay_order_id = 'order_xxxxxx'
    
    context = {
        'order': order,
        'razorpay_order_id': mock_razorpay_order_id, # Use the real ID here
        'amount': amount_in_paise,
        'key_id': settings.RAZORPAY_KEY_ID, # Pass your public key
        'customer_name': shipping_address.name,
        'customer_email': shipping_address.email,
    }
    return render(request, 'store/payment_gateway.html', context)


# --- 4. payment_success (Razorpay Webhook/Callback) ---
def payment_success(request):
    """
    Handles the success response from the Razorpay modal (client-side verification).
    """
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')
    
    # 1. Look up the order using the order ID
    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
    
    # 2. Verify the payment signature (CRITICAL SECURITY STEP)
    # try:
    #     params_dict = {
    #         'razorpay_order_id': razorpay_order_id,
    #         'razorpay_payment_id': razorpay_payment_id,
    #         'razorpay_signature': razorpay_signature
    #     }
    #     RAZORPAY_CLIENT.utility.verify_payment_signature(params_dict)

    #     # Signature is valid. Mark the order as complete/paid.
    #     order.complete = True
    #     order.transaction_id = razorpay_payment_id
    #     order.payment_method = 'Razorpay'
    #     order.status = 'Paid'
    #     order.save()
    #     messages.success(request, "Payment successful! Your order is confirmed.")
        
    # except Exception as e:
    #     # Signature verification failed or other error
    #     messages.error(request, "Payment failed validation. Please contact support.")
    #     order.status = 'Payment_Failed'
    #     order.save()

    # --- For Testing, assume success ---
    order.complete = True
    order.transaction_id = razorpay_payment_id or 'MOCK_RAZORPAY_ID'
    order.payment_method = 'Razorpay'
    order.status = 'Paid'
    order.save()
    
    # Redirect to the final confirmation page
    return redirect('store:order_complete')


# --- 5. order_complete (Final Success Page) ---
def order_complete(request):
    """
    Displays the final order confirmation page after successful payment or COD setup.
    """
    # Get the last completed order for the customer
    order = Order.objects.filter(
        customer=request.user.customer, 
        complete=True
    ).order_by('-date_ordered').first()
    
    if not order:
        # If no completed order is found, redirect back to home
        return redirect('store:home') 
        
    context = {
        'order': order,
        'payment_status': 'PAID' if order.payment_method != 'COD' else 'COD'
    }
    return render(request, 'store/order_complete.html', context)

def removeItem(request, product_id):
    """
    Handles removing an item from the cart.
    This function is called by the URL pattern 'remove_from_cart'.
    """
    # 1. Implement logic to remove the product from the user's cart (session or database)
    
    # 2. Typically redirects back to the cart page after removal
    return redirect('store:cart')