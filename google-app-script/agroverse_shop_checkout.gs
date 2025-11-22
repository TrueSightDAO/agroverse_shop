/**
 * File: google-app-script/agroverse_shop_checkout.gs
 * Repository: https://github.com/TrueSightDAO/agroverse_shop
 * 
 * Description: Handles Stripe checkout session creation, webhook processing, and order management
 * for the Agroverse Shop e-commerce platform. Integrates with Google Sheets for order storage
 * and automated tracking email notifications.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Create a new Google Apps Script project
 * 2. Copy this code into the script editor
 * 3. Set up Script Properties:
 *    - STRIPE_SECRET_KEY (test key for dev, live key for prod)
 *    - STRIPE_WEBHOOK_SECRET (for webhook verification)
 *    - GOOGLE_SHEET_ID (ID of your Google Sheet)
 * 4. Deploy as Web App (Execute as: Me, Who has access: Anyone)
 * 5. Copy the Web App URL to js/config.js
 */

// Configuration - Set these in Script Properties
const CONFIG = {
  stripeSecretKey: PropertiesService.getScriptProperties().getProperty('STRIPE_SECRET_KEY'),
  stripeWebhookSecret: PropertiesService.getScriptProperties().getProperty('STRIPE_WEBHOOK_SECRET'),
  sheetId: PropertiesService.getScriptProperties().getProperty('GOOGLE_SHEET_ID'),
  sheetName: 'Orders' // Name of the sheet tab
};

/**
 * Main doPost handler for web requests
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;

    if (action === 'createCheckoutSession') {
      return createCheckoutSession(data);
    }

    // Handle Stripe webhook
    if (e.parameter && e.parameter['stripe-signature']) {
      return handleStripeWebhook(e);
    }

    return ContentService.createTextOutput(JSON.stringify({
      error: 'Invalid action'
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    Logger.log('Error in doPost: ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Main doGet handler for web requests
 */
function doGet(e) {
  try {
    const action = e.parameter.action;

    if (action === 'getOrderStatus') {
      const sessionId = e.parameter.sessionId;
      return getOrderStatus(sessionId);
    }

    return ContentService.createTextOutput(JSON.stringify({
      error: 'Invalid action'
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    Logger.log('Error in doGet: ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Create Stripe Checkout Session
 */
function createCheckoutSession(data) {
  try {
    const cart = data.cart;
    const shippingAddress = data.shippingAddress;
    const environment = data.environment || 'production';

    if (!cart || !cart.items || cart.items.length === 0) {
      throw new Error('Cart is empty');
    }

    // Build line items for Stripe
    const lineItems = cart.items.map(item => ({
      price: item.stripePriceId,
      quantity: item.quantity
    }));

    // Determine success and cancel URLs based on environment
    const baseUrl = environment === 'development' 
      ? 'http://127.0.0.1:8000' 
      : 'https://www.agroverse.shop';

    const successUrl = `${baseUrl}/order-status?session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrl = `${baseUrl}/checkout`;

    // Create Stripe checkout session
    const payload = {
      mode: 'payment',
      line_items: lineItems,
      success_url: successUrl,
      cancel_url: cancelUrl,
      shipping_address_collection: {
        allowed_countries: ['US']
      },
      billing_address_collection: 'required',
      phone_number_collection: {
        enabled: true
      },
      metadata: {
        cartSessionId: cart.sessionId || '',
        environment: environment,
        source: 'agroverse_shop'
      }
    };

    // Add shipping address if provided
    if (shippingAddress) {
      payload.shipping_address_collection = undefined; // Remove collection since we have it
      payload.shipping_address = {
        line1: shippingAddress.address,
        city: shippingAddress.city,
        state: shippingAddress.state,
        postal_code: shippingAddress.zip,
        country: shippingAddress.country || 'US'
      };
    }

    const response = UrlFetchApp.fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'post',
      headers: {
        'Authorization': 'Bearer ' + CONFIG.stripeSecretKey,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      payload: buildFormData(payload)
    });

    const session = JSON.parse(response.getContentText());

    if (session.error) {
      throw new Error(session.error.message);
    }

    return ContentService.createTextOutput(JSON.stringify({
      checkoutUrl: session.url,
      sessionId: session.id
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    Logger.log('Error creating checkout session: ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Handle Stripe webhook
 */
function handleStripeWebhook(e) {
  try {
    const signature = e.parameter['stripe-signature'];
    const payload = e.postData.contents;

    // Verify webhook signature (simplified - in production, use proper verification)
    // For now, we'll trust the webhook (you should implement proper verification)

    const event = JSON.parse(payload);

    if (event.type === 'checkout.session.completed') {
      const session = event.data.object;
      saveOrderToSheet(session);
    }

    return ContentService.createTextOutput(JSON.stringify({
      received: true
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    Logger.log('Error handling webhook: ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Save order to Google Sheet
 */
function saveOrderToSheet(session) {
  try {
    const sheet = SpreadsheetApp.openById(CONFIG.sheetId).getSheetByName(CONFIG.sheetName);
    
    // Check if order already exists (idempotency)
    const existingRow = findOrderRow(sheet, session.id);
    if (existingRow > 0) {
      Logger.log('Order already exists: ' + session.id);
      return;
    }

    // Extract order data
    const customerEmail = session.customer_details?.email || session.customer_email || '';
    const shippingAddress = session.shipping_details?.address || {};
    const lineItems = session.display_items || [];

    // Format items
    const items = lineItems.map(item => ({
      name: item.custom?.name || item.description || 'Product',
      quantity: item.quantity || 1,
      price: (item.amount || 0) / 100 // Convert from cents
    }));

    // Format shipping address
    const formattedAddress = {
      fullName: session.shipping_details?.name || '',
      address: shippingAddress.line1 || '',
      city: shippingAddress.city || '',
      state: shippingAddress.state || '',
      zip: shippingAddress.postal_code || '',
      country: shippingAddress.country || 'US'
    };

    // Add row to sheet
    const row = [
      session.id, // Session ID (Order ID)
      customerEmail,
      new Date().toISOString(), // Date
      'Placed', // Status
      JSON.stringify(items), // Items
      JSON.stringify(formattedAddress), // Shipping Address
      '', // Tracking Number (empty initially)
      'No', // Email Sent
      new Date().toISOString() // Last Updated
    ];

    sheet.appendRow(row);
    Logger.log('Order saved: ' + session.id);
  } catch (error) {
    Logger.log('Error saving order: ' + error.toString());
    throw error;
  }
}

/**
 * Get order status from Google Sheet
 */
function getOrderStatus(sessionId) {
  try {
    const sheet = SpreadsheetApp.openById(CONFIG.sheetId).getSheetByName(CONFIG.sheetName);
    const row = findOrderRow(sheet, sessionId);

    if (row <= 0) {
      return ContentService.createTextOutput(JSON.stringify({
        error: 'Order not found'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    const data = sheet.getRange(row, 1, 1, 9).getValues()[0];

    const order = {
      sessionId: data[0],
      email: data[1],
      date: data[2],
      status: data[3],
      items: JSON.parse(data[4] || '[]'),
      shippingAddress: JSON.parse(data[5] || '{}'),
      trackingNumber: data[6] || '',
      emailSent: data[7],
      lastUpdated: data[8]
    };

    return ContentService.createTextOutput(JSON.stringify({
      status: 'success',
      order: order
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    Logger.log('Error getting order status: ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Find order row by session ID
 */
function findOrderRow(sheet, sessionId) {
  const data = sheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === sessionId) {
      return i + 1; // Return 1-based row number
    }
  }
  return 0;
}

/**
 * Send tracking emails (scheduled function)
 * Set up a time-driven trigger to run this function periodically
 */
function sendTrackingEmails() {
  try {
    const sheet = SpreadsheetApp.openById(CONFIG.sheetId).getSheetByName(CONFIG.sheetName);
    const data = sheet.getDataRange().getValues();

    // Skip header row
    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      const sessionId = row[0];
      const email = row[1];
      const status = row[3];
      const trackingNumber = row[6];
      const emailSent = row[7];

      // Check if tracking number exists and email not sent
      if (trackingNumber && trackingNumber.trim() && emailSent !== 'Yes') {
        sendTrackingEmail(email, sessionId, trackingNumber, status);
        
        // Mark email as sent
        sheet.getRange(i + 1, 8).setValue('Yes');
        sheet.getRange(i + 1, 9).setValue(new Date().toISOString());
      }
    }
  } catch (error) {
    Logger.log('Error sending tracking emails: ' + error.toString());
  }
}

/**
 * Send tracking email to customer
 */
function sendTrackingEmail(email, sessionId, trackingNumber, status) {
  try {
    const trackingUrl = getTrackingUrl(trackingNumber);
    
    const subject = 'Your Agroverse Order Has Shipped!';
    const body = `
Hello,

Your order (${sessionId}) has been shipped!

Tracking Number: ${trackingNumber}
${trackingUrl ? `Track your package: ${trackingUrl}` : ''}

Status: ${status}

Thank you for your purchase!

Best regards,
Agroverse Team
    `.trim();

    MailApp.sendEmail({
      to: email,
      subject: subject,
      body: body
    });

    Logger.log('Tracking email sent to: ' + email);
  } catch (error) {
    Logger.log('Error sending email: ' + error.toString());
  }
}

/**
 * Get tracking URL based on tracking number format
 */
function getTrackingUrl(trackingNumber) {
  const trimmed = trackingNumber.trim().toUpperCase();

  // USPS
  if (/^\d+[A-Z]{2}\d+US$/.test(trimmed)) {
    return `https://tools.usps.com/go/TrackConfirmAction?tLabels=${trimmed}`;
  }

  // UPS
  if (trimmed.startsWith('1Z')) {
    return `https://www.ups.com/track?tracknum=${trimmed}`;
  }

  // FedEx
  if (/^\d{12}$/.test(trimmed)) {
    return `https://www.fedex.com/fedextrack/?trknbr=${trimmed}`;
  }

  // Default: USPS
  return `https://tools.usps.com/go/TrackConfirmAction?tLabels=${trimmed}`;
}

/**
 * Helper: Build form data for Stripe API
 */
function buildFormData(data) {
  const params = [];
  for (const key in data) {
    if (data[key] !== undefined && data[key] !== null) {
      if (typeof data[key] === 'object') {
        params.push(key + '=' + encodeURIComponent(JSON.stringify(data[key])));
      } else {
        params.push(key + '=' + encodeURIComponent(data[key]));
      }
    }
  }
  return params.join('&');
}

