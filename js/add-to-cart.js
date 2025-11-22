/**
 * Add to Cart Button Handler
 * Handles "Add to Cart" button clicks on product pages
 */

(function() {
  'use strict';

  /**
   * Show toast notification
   */
  function showToast(message) {
    // Remove existing toast if any
    const existingToast = document.getElementById('add-to-cart-toast');
    if (existingToast) {
      existingToast.remove();
    }

    // Create toast
    const toast = document.createElement('div');
    toast.id = 'add-to-cart-toast';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: var(--color-primary, #3b3333);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 8px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
      z-index: 3000;
      animation: slideIn 0.3s ease;
      font-weight: 600;
    `;

    // Add animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }
    `;
    if (!document.getElementById('toast-animations')) {
      style.id = 'toast-animations';
      document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 3000);
  }

  /**
   * Handle add to cart button click
   */
  function handleAddToCart(event) {
    event.preventDefault();

    const button = event.target.closest('.add-to-cart-btn');
    if (!button) return;

    // Get product data from data attributes
    const product = {
      productId: button.dataset.productId,
      name: button.dataset.productName,
      price: parseFloat(button.dataset.productPrice),
      image: button.dataset.productImage,
      stripePriceId: button.dataset.stripePriceId || '',
      quantity: 1
    };

    // Validate product data
    if (!product.productId || !product.name || !product.price) {
      console.error('Invalid product data:', product);
      showToast('Error: Invalid product data');
      return;
    }

    // Add to cart
    const success = window.Cart.add(product);

    if (success) {
      showToast('Added to cart!');
      
      // Optionally open cart sidebar
      if (window.CartUI) {
        setTimeout(() => {
          window.CartUI.open();
        }, 500);
      }
    } else {
      showToast('Failed to add to cart. Please try again.');
    }
  }

  /**
   * Initialize add to cart buttons
   */
  function initAddToCart() {
    // Attach event listeners to all add to cart buttons
    document.addEventListener('click', function(event) {
      if (event.target.closest('.add-to-cart-btn')) {
        handleAddToCart(event);
      }
    });

    // Also handle buttons that might be added dynamically
    const buttons = document.querySelectorAll('.add-to-cart-btn');
    buttons.forEach(button => {
      button.addEventListener('click', handleAddToCart);
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAddToCart);
  } else {
    initAddToCart();
  }

})();

