/**
 * Shopping Cart Management
 * Handles cart operations using localStorage
 */

(function() {
  'use strict';

  const CART_STORAGE_KEY = 'agroverse_cart';
  const CART_EVENT_NAME = 'cartUpdated';

  /**
   * Generate unique session ID
   */
  function generateSessionId() {
    return `cart_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get cart from localStorage
   */
  function getCart() {
    try {
      const cartData = localStorage.getItem(CART_STORAGE_KEY);
      if (!cartData) {
        return {
          sessionId: generateSessionId(),
          items: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
      }
      return JSON.parse(cartData);
    } catch (error) {
      console.error('Error reading cart:', error);
      return {
        sessionId: generateSessionId(),
        items: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
    }
  }

  /**
   * Save cart to localStorage
   */
  function saveCart(cart) {
    try {
      cart.updatedAt = new Date().toISOString();
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
      
      // Dispatch custom event for UI updates
      window.dispatchEvent(new CustomEvent(CART_EVENT_NAME, {
        detail: { cart: cart }
      }));
      
      return true;
    } catch (error) {
      console.error('Error saving cart:', error);
      return false;
    }
  }

  /**
   * Add item to cart
   */
  function addToCart(product) {
    const cart = getCart();
    
    // Validate product data
    if (!product.productId || !product.name || !product.price) {
      console.error('Invalid product data:', product);
      return false;
    }

    // Check if product already in cart
    const existingIndex = cart.items.findIndex(
      item => item.productId === product.productId
    );

    if (existingIndex >= 0) {
      // Update quantity
      cart.items[existingIndex].quantity += (product.quantity || 1);
    } else {
      // Add new item
      cart.items.push({
        productId: product.productId,
        name: product.name,
        price: parseFloat(product.price),
        quantity: product.quantity || 1,
        image: product.image || '',
        stripePriceId: product.stripePriceId || ''
      });
    }

    return saveCart(cart);
  }

  /**
   * Remove item from cart
   */
  function removeFromCart(productId) {
    const cart = getCart();
    cart.items = cart.items.filter(item => item.productId !== productId);
    return saveCart(cart);
  }

  /**
   * Update item quantity
   */
  function updateQuantity(productId, quantity) {
    if (quantity <= 0) {
      return removeFromCart(productId);
    }

    const cart = getCart();
    const item = cart.items.find(item => item.productId === productId);
    
    if (item) {
      item.quantity = parseInt(quantity, 10);
      return saveCart(cart);
    }
    
    return false;
  }

  /**
   * Clear cart
   */
  function clearCart() {
    const cart = {
      sessionId: generateSessionId(),
      items: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    return saveCart(cart);
  }

  /**
   * Get cart item count
   */
  function getCartItemCount() {
    const cart = getCart();
    return cart.items.reduce((total, item) => total + item.quantity, 0);
  }

  /**
   * Calculate subtotal
   */
  function calculateSubtotal() {
    const cart = getCart();
    return cart.items.reduce((total, item) => {
      return total + (item.price * item.quantity);
    }, 0);
  }

  /**
   * Get cart data
   */
  function getCartData() {
    return getCart();
  }

  // Export public API
  window.Cart = {
    add: addToCart,
    remove: removeFromCart,
    updateQuantity: updateQuantity,
    clear: clearCart,
    getItemCount: getCartItemCount,
    getSubtotal: calculateSubtotal,
    getCart: getCartData,
    EVENT_NAME: CART_EVENT_NAME
  };

})();

