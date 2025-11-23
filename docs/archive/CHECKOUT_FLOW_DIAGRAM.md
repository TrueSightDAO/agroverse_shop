# Checkout Flow - Visual Diagram

## Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER BROWSES PRODUCTS                        │
│  (Product pages, Category pages)                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   CLICKS "ADD TO CART" │
              └──────────┬─────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  ITEM ADDED TO localStorage        │
        │  - Product ID, Name, Price, Qty   │
        │  - Cart icon badge updates        │
        │  - Cart persists across sessions   │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  USER CLICKS CART ICON     │
        │  Cart drawer/sidebar opens│
        └────────────┬───────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │  USER REVIEWS CART         │
        │  - Can update quantities    │
        │  - Can remove items        │
        │  - Sees subtotal           │
        └────────────┬───────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │  CLICKS "CHECKOUT"          │
        └────────────┬───────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              CHECKOUT PAGE (/checkout/index.html)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Shipping Address Form:                                  │  │
│  │  - Full Name                                            │  │
│  │  - Email                                                │  │
│  │  - Phone                                                │  │
│  │  - Address, City, State, ZIP                            │  │
│  │                                                          │  │
│  │  Order Summary:                                         │  │
│  │  - Items list                                           │  │
│  │  - Subtotal                                             │  │
│  │                                                          │  │
│  │  [Continue to Payment]                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  FRONTEND CALLS GOOGLE APP SCRIPT   │
        │  POST /exec                         │
        │  {                                  │
        │    action: "createCheckoutSession", │
        │    cart: [...],                     │
        │    shippingAddress: {...}            │
        │  }                                  │
        └────────────┬─────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE APP SCRIPT                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  1. Validates cart data                                   │ │
│  │  2. Creates Stripe Checkout Session:                     │ │
│  │     - Line items from cart                                │ │
│  │     - Shipping address                                    │ │
│  │     - Success URL: /order-status?session_id={ID}         │ │
│  │     - Cancel URL: /checkout                               │ │
│  │  3. Returns checkout URL                                  │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  FRONTEND RECEIVES CHECKOUT URL     │
        │  Redirects user to Stripe           │
        └────────────┬─────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              STRIPE CHECKOUT PAGE                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  - Payment method selection                               │ │
│  │  - Shipping address confirmation                          │ │
│  │  - Order summary                                          │ │
│  │  - Secure payment processing                              │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  USER COMPLETES PAYMENT              │
        │  Stripe processes payment            │
        └────────────┬─────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────────┐
        │  STRIPE WEBHOOK FIRES               │
        │  checkout.session.completed event    │
        └────────────┬─────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE APP SCRIPT (Webhook Handler)                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  1. Verifies webhook signature                           │ │
│  │  2. Extracts order data from Stripe session              │ │
│  │  3. Writes to Google Sheets:                             │ │
│  │     - Session ID (unique key)                            │ │
│  │     - Customer email                                     │ │
│  │     - Shipping address                                   │ │
│  │     - Items (JSON)                                       │ │
│  │     - Status: "Placed"                                   │ │
│  │     - Date: timestamp                                    │ │
│  │     - Tracking Number: (empty)                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  STRIPE REDIRECTS TO SUCCESS URL     │
        │  /order-status?session_id=cs_xxx     │
        └────────────┬─────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ORDER STATUS PAGE                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Frontend calls Google App Script:                       │  │
│  │  GET /exec?action=getOrderStatus&sessionId=cs_xxx       │  │
│  │                                                          │  │
│  │  Displays:                                               │  │
│  │  ✓ Order Placed                                         │  │
│  │  - Order number                                          │  │
│  │  - Items summary                                         │  │
│  │  - Shipping address                                      │  │
│  │  - Status: "Placed"                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

                    [TIME PASSES]

┌─────────────────────────────────────────────────────────────────┐
│              ADMIN WORKFLOW                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Admin opens Google Sheet                             │  │
│  │  2. Finds order row by Session ID                        │  │
│  │  3. Enters tracking number in "Tracking Number" column  │  │
│  │  4. Saves sheet                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  GOOGLE APP SCRIPT (Scheduled)       │
        │  Runs every hour or on edit          │
        └────────────┬─────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE APP SCRIPT (Email Sender)                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  1. Scans Google Sheets for:                             │ │
│  │     - Tracking Number present                            │ │
│  │     - Email not yet sent                                 │ │
│  │                                                          │ │
│  │  2. For each order:                                      │ │
│  │     - Retrieves customer email                          │ │
│  │     - Retrieves tracking number                          │ │
│  │     - Composes email with:                               │ │
│  │       * Order confirmation                               │ │
│  │       * Tracking number                                  │ │
│  │       * Tracking link (USPS/UPS/FedEx)                   │ │
│  │     - Sends via Gmail API                                │ │
│  │     - Marks as sent                                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

                    [USER RETURNS LATER]

┌─────────────────────────────────────────────────────────────────┐
│              USER VISITS ORDER STATUS PAGE                      │
│  /order-status?session_id=cs_xxx                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Frontend calls Google App Script                        │  │
│  │  GET /exec?action=getOrderStatus&sessionId=cs_xxx        │  │
│  │                                                          │  │
│  │  Displays:                                               │  │
│  │  ✓ Order Shipped                                         │  │
│  │  - Order number                                          │  │
│  │  - Items summary                                         │  │
│  │  - Shipping address                                      │  │
│  │  - Status: "Shipped"                                     │  │
│  │  - Tracking Number: 1Z999AA101...                       │  │
│  │  - [Track Package] link                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Data Structures

### Cart (localStorage)
```json
{
  "sessionId": "cart_20250115_abc123",
  "items": [
    {
      "productId": "oscar-bahia-200g",
      "name": "Ceremonial Cacao – Oscar's Farm",
      "price": 25.00,
      "quantity": 2,
      "image": "/assets/images/products/oscars-farm.jpeg",
      "stripePriceId": "price_xxxxx"
    }
  ],
  "createdAt": "2025-01-15T10:30:00Z",
  "updatedAt": "2025-01-15T10:35:00Z"
}
```

### Google Sheets Row
```
| Session ID | Email              | Date       | Status  | Items (JSON) | Shipping Address (JSON) | Tracking Number | Email Sent | Last Updated |
|------------|-------------------|------------|---------|-------------|------------------------|-----------------|------------|--------------|
| cs_xxx     | user@example.com  | 2025-01-15 | Shipped | {...}       | {...}                  | 1Z999AA101...   | Yes        | 2025-01-16   |
```

### Stripe Checkout Session Metadata
```json
{
  "metadata": {
    "sessionId": "cart_20250115_abc123",
    "source": "agroverse_shop"
  }
}
```

## State Transitions

```
Order Status Flow:
Placed → Processing → Shipped → Delivered

Tracking Email Flow:
Tracking Added → Email Queued → Email Sent
```

