# Checkout UX Implementation Plan

## Overview
This document outlines the UX flow and implementation approach for the Agroverse Shop checkout system using:
- **Frontend**: Static HTML/JS on GitHub Pages
- **Payment**: Stripe Checkout
- **Database**: Google Sheets
- **Backend Processing**: Google App Script

---

## User Flow

### 1. Shopping Cart Experience

#### 1.1 Add to Cart
- **Location**: Product pages and category pages
- **Action**: User clicks "Add to Cart" button
- **Behavior**:
  - Product added to cart (stored in `localStorage`)
  - Cart icon in header shows item count badge
  - Optional: Brief toast notification "Added to cart"
  - Cart persists across sessions (localStorage)

#### 1.2 Cart Storage Structure
```javascript
{
  items: [
    {
      productId: "oscar-bahia-200g",
      name: "Ceremonial Cacao – Oscar's Farm, Bahia Brazil, 2024 (200g)",
      price: 25.00,
      quantity: 2,
      image: "/assets/images/products/oscars-farm.jpeg",
      stripePriceId: "price_xxxxx" // Stripe Price ID
    }
  ],
  sessionId: "unique-session-id", // Generated on first add
  createdAt: "2025-01-XX",
  updatedAt: "2025-01-XX"
}
```

#### 1.3 Cart Icon & Badge
- **Location**: Header navigation (always visible)
- **Display**: Shopping cart icon with item count badge
- **Click**: Opens cart sidebar/drawer

#### 1.4 Cart Sidebar/Drawer
- **Layout**: Slide-in from right (mobile) or overlay (desktop)
- **Contents**:
  - List of cart items with:
    - Product image (thumbnail)
    - Product name
    - Quantity selector (+/- buttons)
    - Price per item
    - Remove button
  - Subtotal
  - "Proceed to Checkout" button
- **Features**:
  - Update quantities inline
  - Remove items
  - Auto-calculate totals
  - Close button/overlay click to dismiss

---

### 2. Checkout Flow

#### 2.1 Pre-Checkout Page (Shipping Address Collection)
- **URL**: `/checkout/index.html`
- **Purpose**: Collect shipping address before redirecting to Stripe
- **Form Fields**:
  - Full Name
  - Email Address
  - Phone Number
  - Street Address
  - City
  - State
  - ZIP Code
  - Country (default: USA)
- **Validation**: Client-side validation before proceeding
- **Action**: "Continue to Payment" button

#### 2.2 Stripe Checkout Session Creation
- **Process**:
  1. Frontend sends cart data + shipping address to Google App Script endpoint
  2. Google App Script creates Stripe Checkout Session with:
     - Line items from cart
     - Shipping address pre-filled
     - Success URL: `https://www.agroverse.shop/order-status?session_id={CHECKOUT_SESSION_ID}`
     - Cancel URL: `https://www.agroverse.shop/checkout`
  3. Google App Script returns Stripe Checkout Session URL
  4. Frontend redirects user to Stripe

#### 2.3 Stripe Checkout
- **Experience**: Stripe-hosted checkout page
- **Features**:
  - Payment method selection
  - Shipping address confirmation
  - Order summary
  - Secure payment processing

---

### 3. Post-Checkout Experience

#### 3.1 Order Status Page
- **URL**: `/order-status/index.html?session_id={STRIPE_SESSION_ID}`
- **Purpose**: Show order confirmation and status
- **Initial State** (immediately after checkout):
  - "Order Placed" status
  - Order number (from Stripe)
  - Order summary (items, quantities, prices)
  - Shipping address
  - Estimated delivery date
  - "Thank you for your order!" message

#### 3.2 Order Status Persistence
- **Storage**: Google Sheets row with:
  - Stripe Session ID (unique identifier)
  - Customer Email
  - Order Date
  - Order Status (Placed, Processing, Shipped, Delivered)
  - Shipping Address (full)
  - Items (JSON or comma-separated)
  - Tracking Number (added by admin)
  - Last Updated timestamp

#### 3.3 Returning User Experience
- **URL**: `/order-status/index.html?session_id={STRIPE_SESSION_ID}`
- **Behavior**:
  1. Page loads with session_id from URL
  2. Frontend calls Google App Script endpoint to fetch order status
  3. Google App Script reads from Google Sheets
  4. Display current order status:
     - If tracking number exists: Show tracking info with link
     - Show current status badge (Placed/Processing/Shipped/Delivered)
     - Show order details

---

### 4. Admin Workflow

#### 4.1 Google Sheets Structure
```
| Order ID | Email | Date | Status | Items | Shipping Address | Tracking Number | Last Updated |
|----------|-------|------|--------|-------|------------------|-----------------|--------------|
| cs_xxx   | ...   | ...  | Shipped| ...   | ...              | 1Z999AA101...   | 2025-01-XX   |
```

#### 4.2 Adding Tracking Number
- Admin opens Google Sheet
- Finds order row
- Enters tracking number in "Tracking Number" column
- Saves

#### 4.3 Automated Email Notification
- **Trigger**: Google App Script runs periodically (e.g., every hour) or on edit
- **Process**:
  1. Scans Google Sheet for rows where:
     - Tracking Number is newly added (not empty, not previously sent)
     - Email notification not sent
  2. For each matching row:
     - Retrieve customer email
     - Retrieve tracking number
     - Retrieve order details
     - Send email via Gmail API with:
       - Order confirmation
       - Tracking number
       - Tracking link (USPS/UPS/FedEx based on format)
  3. Mark email as sent (add "Email Sent" column or timestamp)

---

## Technical Implementation

### Frontend Components

#### 1. Cart Management (`js/cart.js`)
```javascript
// Functions:
- addToCart(product)
- removeFromCart(productId)
- updateQuantity(productId, quantity)
- getCart()
- clearCart()
- getCartItemCount()
- calculateSubtotal()
```

#### 2. Checkout Page (`checkout/index.html`)
- Form validation
- Cart display
- Shipping address form
- Stripe session creation API call
- Redirect to Stripe

#### 3. Order Status Page (`order-status/index.html`)
- Fetch order status from Google App Script
- Display order details
- Show tracking information if available
- Handle loading/error states

#### 4. Cart UI Component
- Cart icon with badge in header
- Cart sidebar/drawer
- Cart item list component
- Quantity selectors

---

### Google App Script Functions

#### 1. Create Stripe Checkout Session
- **Endpoint**: `POST /exec` (Google Apps Script Web App)
- **Input**: 
  ```json
  {
    "action": "createCheckoutSession",
    "cart": [...],
    "shippingAddress": {...}
  }
  ```
- **Process**:
  1. Validate cart data
  2. Create Stripe Checkout Session via Stripe API
  3. Return session URL
- **Output**: `{ "checkoutUrl": "https://checkout.stripe.com/..." }`

#### 2. Get Order Status
- **Endpoint**: `GET /exec?action=getOrderStatus&sessionId=cs_xxx`
- **Process**:
  1. Query Google Sheets for order by session_id
  2. Return order data
- **Output**: 
  ```json
  {
    "status": "success",
    "order": {
      "sessionId": "cs_xxx",
      "email": "...",
      "status": "Shipped",
      "trackingNumber": "1Z999AA101...",
      "items": [...],
      "shippingAddress": {...}
    }
  }
  ```

#### 3. Process Stripe Webhook
- **Endpoint**: `POST /exec` (triggered by Stripe)
- **Process**:
  1. Verify webhook signature
  2. On `checkout.session.completed`:
     - Extract order details from Stripe session
     - Write to Google Sheets:
       - Session ID
       - Customer email
       - Shipping address
       - Items (from line items)
       - Status: "Placed"
       - Date: current timestamp
  3. Return 200 OK

#### 4. Send Tracking Emails (Scheduled)
- **Trigger**: Time-driven trigger (every hour) or on edit
- **Process**:
  1. Scan Google Sheets for orders with:
     - Tracking number present
     - Email not yet sent
  2. For each order:
     - Compose email with order details and tracking
     - Send via Gmail API
     - Mark as sent (update "Email Sent" column)

---

## File Structure

```
agroverse_shop/
├── checkout/
│   └── index.html          # Pre-checkout shipping form
├── order-status/
│   └── index.html          # Order status page
├── js/
│   ├── cart.js             # Cart management
│   ├── checkout.js        # Checkout logic
│   └── order-status.js    # Order status fetching
├── css/
│   └── cart.css           # Cart UI styles
└── product-page/
    └── [products]/
        └── index.html      # Updated with "Add to Cart" buttons
```

---

## Data Flow Diagram

```
User adds item → localStorage → Cart UI updates
                ↓
User clicks checkout → Checkout page (shipping form)
                ↓
User submits → Google App Script (creates Stripe session)
                ↓
Redirect to Stripe → User pays
                ↓
Stripe webhook → Google App Script → Write to Google Sheets
                ↓
Redirect to order-status page → Fetch from Google Sheets → Display
                ↓
Admin adds tracking → Google Sheet updated
                ↓
Scheduled script runs → Send email to customer
```

---

## Security Considerations

1. **Stripe API Keys**: Store in Google App Script Properties (not in frontend)
2. **Webhook Verification**: Verify Stripe webhook signatures
3. **Input Validation**: Validate all user inputs
4. **Rate Limiting**: Consider rate limiting on Google App Script endpoints
5. **CORS**: Configure CORS for Google App Script web app

---

## UX Enhancements

1. **Loading States**: Show spinners during API calls
2. **Error Handling**: User-friendly error messages
3. **Empty Cart State**: Helpful message when cart is empty
4. **Mobile Optimization**: Responsive cart drawer
5. **Accessibility**: ARIA labels, keyboard navigation
6. **Order History**: Future enhancement - allow users to view all their orders by email

---

## Testing Checklist

- [ ] Add item to cart
- [ ] Update quantity in cart
- [ ] Remove item from cart
- [ ] Cart persists across page refreshes
- [ ] Checkout form validation
- [ ] Stripe checkout session creation
- [ ] Stripe payment flow
- [ ] Webhook processing
- [ ] Order status page displays correctly
- [ ] Returning user can view order status
- [ ] Admin can add tracking number
- [ ] Email notification sent when tracking added
- [ ] Mobile responsiveness

---

## Next Steps

1. Create cart management JavaScript
2. Build checkout page
3. Build order status page
4. Set up Google App Script with Stripe integration
5. Configure Google Sheets structure
6. Set up Stripe webhook
7. Implement email notification system
8. Test end-to-end flow
9. Deploy to GitHub Pages

