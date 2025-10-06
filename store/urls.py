# store/urls.py

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Basic Views
    path('', views.home, name='home'),
    path('cart/', views.cart_view, name='cart'),
    
    
     # AJAX ENDPOINT: Uses the newly renamed function (if you renamed it to updateCartAjax)
    path('update_item/', views.updateCartAjax, name='update_item'), 
    
    # QUANTITY UPDATE FORM: Uses the new function
    path('update_cart/<int:product_id>/', views.updateCartPage, name='update_cart'),
    
    # REMOVAL LINK: Uses the new function
    path('remove_from_cart/<int:product_id>/', views.updateCartPage, name='remove_from_cart'),

    # Product Detail 
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Checkout & Payment Integration
    path('checkout/', views.checkout_view, name='checkout'), 
    # 1. Final Review/Payment Method Confirmation (Where user is redirected after POST from checkout)
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    
    # 2. Online Payment Processor endpoint (Razorpay/Payment Gateway)
    path('process_razorpay_payment/', views.process_razorpay_payment, name='process_razorpay_payment'),
    
    # 3. Finalize COD Order endpoint
    path('finalize_cod_order/', views.finalize_cod_order, name='finalize_cod_order'),

    # 4. Payment Success/Verification endpoint (Razorpay sends data here)
    path('payment_success/', views.payment_success, name='payment_success'),

    # 5. Final Confirmation Page (Common success page for all orders)
    path('order_complete/', views.order_complete, name='order_complete'),

    # --- END E-COMMERCE WORKFLOW ---
    
    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    
    # Filtering
    path('category/<slug:category_slug>/', views.home, name='category_filter'),

    # Static Pages
    # The 'about' URL definition which the template was looking for
    path('about-us/', views.about, name='about'),
    # The 'contact' URL definition (for completeness)
    path('contact-us/', views.contact, name='contact'),
]