from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from decimal import Decimal
# Model 1: Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-populate slug if it's not set
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


# Model 2: Product
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True) 
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=False)

    def __str__(self):
        return self.name


# models.py

from django.contrib.auth.models import User
from django.db import models

class Customer(models.Model):
    # This is the crucial link. It creates a one-to-one relationship
    # and allows you to access the User *from* the Customer, 
    # but not necessarily the other way around by default.
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)
    # ... other customer-specific fields
    
    def __str__(self):
        return self.user.username

# Model 3: Order (The Shopping Cart or Completed Purchase)
class Order(models.Model):
    # Order linked to a User, can be null for Guest/Session Cart
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    # This ID will be used for Razorpay transactions
    transaction_id = models.CharField(max_length=100, null=True) 
    get_total_with_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        """Calculates the total value of all items in the order."""
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems]) 
        return total
    
    @property
    def get_cart_items(self):
        """Calculates the total quantity of all items in the order (for the navbar count)."""
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    def get_total_with_shipping(self):
        """
        Calculates the final total, setting shipping to 0.00 (free).
        """
        subtotal = self.get_cart_total
        shipping_cost = Decimal('0.00')
        
        # Ensure subtotal is a numerical type (like Decimal or float) for addition
        return subtotal + shipping_cost 


# Model 4: OrderItem (A single product line item in an Order)
class OrderItem(models.Model):
    # --- IMPORTANT: Using string references for local models to prevent E300 error ---
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True) 
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True)
    
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    @property
    def get_total(self):
        """Calculates the total price for a single order item."""
        # Note: self.product will be the actual object once the ORM loads
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, null=False) # Maps to full_name from form
    email = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=False)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address