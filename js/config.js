/**
 * Environment Configuration
 * Automatically detects local development vs production
 */

(function() {
  'use strict';

  // Detect environment based on hostname
  const isLocal = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' ||
                  window.location.hostname.includes('localhost:') ||
                  window.location.hostname.includes('127.0.0.1:');

  const isProduction = window.location.hostname === 'www.agroverse.shop' ||
                       window.location.hostname === 'agroverse.shop' ||
                       window.location.hostname.includes('github.io');

  // Base URL configuration
  const baseUrl = isLocal 
    ? 'http://127.0.0.1:8000' // Local development server
    : 'https://www.agroverse.shop';

  // Google App Script Web App URL
  // Replace with your actual Google App Script deployment URL
  const GOOGLE_SCRIPT_URL = isLocal
    ? 'YOUR_LOCAL_DEV_SCRIPT_URL' // For testing, you can use a test script
    : 'YOUR_PRODUCTION_SCRIPT_URL'; // Your production Google App Script URL

  // Stripe Configuration
  // Note: Stripe keys should be in Google App Script, not here
  // This is just for reference
  const STRIPE_CONFIG = {
    mode: isLocal ? 'test' : 'live',
    publishableKey: isLocal 
      ? 'pk_test_...' // Stripe test publishable key (optional, for future use)
      : 'pk_live_...' // Stripe live publishable key (optional, for future use)
  };

  // Export configuration
  window.AGROVERSE_CONFIG = {
    isLocal: isLocal,
    isProduction: isProduction,
    baseUrl: baseUrl,
    googleScriptUrl: GOOGLE_SCRIPT_URL,
    stripe: STRIPE_CONFIG,
    environment: isLocal ? 'development' : 'production',
    
    // URLs
    urls: {
      checkout: `${baseUrl}/checkout`,
      orderStatus: `${baseUrl}/order-status`,
      cart: `${baseUrl}/#cart`
    },
    
    // Debug mode
    debug: isLocal
  };

  // Log environment in development
  if (isLocal) {
    console.log('🔧 Development Mode');
    console.log('Config:', window.AGROVERSE_CONFIG);
  }
})();

