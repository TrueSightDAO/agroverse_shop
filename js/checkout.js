/**
 * Checkout Process
 * Handles checkout form and Stripe session creation
 */

(function() {
  'use strict';

  const config = window.AGROVERSE_CONFIG || {};

  /**
   * Validate shipping address form
   */
  function validateShippingForm(formData) {
    const errors = [];

    if (!formData.fullName || formData.fullName.trim().length < 2) {
      errors.push('Full name is required');
    }

    if (!formData.email || !formData.email.includes('@')) {
      errors.push('Valid email is required');
    }

    if (!formData.phone || formData.phone.trim().length < 10) {
      errors.push('Valid phone number is required');
    }

    if (!formData.address || formData.address.trim().length < 5) {
      errors.push('Street address is required');
    }

    if (!formData.city || formData.city.trim().length < 2) {
      errors.push('City is required');
    }

    if (!formData.state || formData.state.trim().length < 2) {
      errors.push('State is required');
    }

    if (!formData.zip || !/^\d{5}(-\d{4})?$/.test(formData.zip)) {
      errors.push('Valid ZIP code is required');
    }

    if (!formData.country) {
      errors.push('Country is required');
    }

    return {
      valid: errors.length === 0,
      errors: errors
    };
  }

  /**
   * Get form data
   */
  function getFormData(form) {
    return {
      fullName: form.querySelector('[name="fullName"]')?.value || '',
      email: form.querySelector('[name="email"]')?.value || '',
      phone: form.querySelector('[name="phone"]')?.value || '',
      address: form.querySelector('[name="address"]')?.value || '',
      city: form.querySelector('[name="city"]')?.value || '',
      state: form.querySelector('[name="state"]')?.value || '',
      zip: form.querySelector('[name="zip"]')?.value || '',
      country: form.querySelector('[name="country"]')?.value || 'US'
    };
  }

  /**
   * Show form errors
   */
  function showErrors(errors) {
    const errorContainer = document.getElementById('checkout-errors');
    if (errorContainer) {
      errorContainer.innerHTML = errors.map(err => 
        `<div class="error-message">${err}</div>`
      ).join('');
      errorContainer.style.display = 'block';
    }
  }

  /**
   * Clear form errors
   */
  function clearErrors() {
    const errorContainer = document.getElementById('checkout-errors');
    if (errorContainer) {
      errorContainer.innerHTML = '';
      errorContainer.style.display = 'none';
    }
  }

  /**
   * Show loading state
   */
  function setLoading(loading) {
    const submitButton = document.getElementById('checkout-submit');
    const form = document.getElementById('checkout-form');
    
    if (submitButton) {
      submitButton.disabled = loading;
      submitButton.textContent = loading ? 'Processing...' : 'Continue to Payment';
    }
    
    if (form) {
      const inputs = form.querySelectorAll('input, select');
      inputs.forEach(input => input.disabled = loading);
    }
  }

  /**
   * Create Stripe checkout session via Google App Script
   */
  async function createCheckoutSession(cart, shippingAddress) {
    const scriptUrl = config.googleScriptUrl;
    
    if (!scriptUrl || scriptUrl.includes('YOUR_')) {
      throw new Error('Google App Script URL not configured. Please set AGROVERSE_CONFIG.googleScriptUrl');
    }

    const payload = {
      action: 'createCheckoutSession',
      cart: cart,
      shippingAddress: shippingAddress,
      environment: config.environment
    };

    try {
      const response = await fetch(scriptUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(errorData || 'Failed to create checkout session');
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      if (!data.checkoutUrl) {
        throw new Error('No checkout URL received');
      }

      return data.checkoutUrl;
    } catch (error) {
      console.error('Checkout session creation error:', error);
      throw error;
    }
  }

  /**
   * Handle form submission
   */
  async function handleCheckoutSubmit(event) {
    event.preventDefault();
    clearErrors();

    const form = event.target;
    const formData = getFormData(form);

    // Validate form
    const validation = validateShippingForm(formData);
    if (!validation.valid) {
      showErrors(validation.errors);
      return;
    }

    // Check cart
    const cart = window.Cart.getCart();
    if (!cart.items || cart.items.length === 0) {
      showErrors(['Your cart is empty']);
      return;
    }

    // Show loading
    setLoading(true);

    try {
      // Create checkout session
      const checkoutUrl = await createCheckoutSession(cart, formData);
      
      // Redirect to Stripe
      window.location.href = checkoutUrl;
    } catch (error) {
      console.error('Checkout error:', error);
      showErrors([error.message || 'Failed to process checkout. Please try again.']);
      setLoading(false);
    }
  }

  /**
   * Initialize checkout page
   */
  function initCheckout() {
    const form = document.getElementById('checkout-form');
    if (form) {
      form.addEventListener('submit', handleCheckoutSubmit);
    }

    // Update cart display
    updateCartDisplay();
  }

  /**
   * Update cart display on checkout page
   */
  function updateCartDisplay() {
    const cart = window.Cart.getCart();
    const cartItemsContainer = document.getElementById('checkout-cart-items');
    const cartSubtotal = document.getElementById('checkout-subtotal');

    if (cartItemsContainer) {
      if (cart.items.length === 0) {
        cartItemsContainer.innerHTML = '<p>Your cart is empty</p>';
      } else {
        cartItemsContainer.innerHTML = cart.items.map(item => `
          <div class="checkout-cart-item">
            <img src="${item.image || ''}" alt="${item.name}" class="checkout-cart-item-image">
            <div class="checkout-cart-item-details">
              <div class="checkout-cart-item-name">${item.name}</div>
              <div class="checkout-cart-item-quantity">Quantity: ${item.quantity}</div>
            </div>
            <div class="checkout-cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
          </div>
        `).join('');
      }
    }

    if (cartSubtotal) {
      const subtotal = window.Cart.getSubtotal();
      cartSubtotal.textContent = `$${subtotal.toFixed(2)}`;
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCheckout);
  } else {
    initCheckout();
  }

  // Export for external use
  window.Checkout = {
    validateShippingForm: validateShippingForm,
    createCheckoutSession: createCheckoutSession
  };

})();

