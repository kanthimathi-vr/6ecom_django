// store/static/js/cart.js

// 1. Helper function to get the CSRF token from cookies
function getCookie(name) {
    var cookieArr = document.cookie.split(";");
    for(var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        if(name == cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}

// 2. Main function to update the user's cart (order)
function updateUserOrder(productId, action) {
    console.log('Sending data to backend...');

    var url = '/update_item/'; // The URL we'll define in urls.py

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // CSRF Token is mandatory for POST requests
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        // Update the cart count in the navbar with the count from the Django response
        document.getElementById('cart-count').innerText = data.cart_items;
        console.log('Cart updated. New count:', data.cart_items);
        
        // Optional: If the user is on the cart page, reload it to show the change
        if (window.location.pathname.includes('/cart/')) {
             window.location.reload(); 
        }
    });
}

// 3. Attach click handlers to all "Add to Cart" buttons
document.addEventListener('DOMContentLoaded', function() {
    var updateBtns = document.getElementsByClassName('update-cart');

    for (var i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function() {
            var productId = this.dataset.product;
            var action = this.dataset.action;
            
            if (user === 'AnonymousUser') {
                alert('Please log in or implement session cart for guests!');
            } else {
                updateUserOrder(productId, action);
            }
        });
    }

    // Initialize cart count on load using the context value
    document.getElementById('cart-count').innerText = initialCartCount; 
});