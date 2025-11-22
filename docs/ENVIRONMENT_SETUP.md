# Environment Setup - Development vs Production

## Quick Overview

The system automatically detects whether you're in **development** or **production** mode based on the hostname:

- **Development**: `localhost`, `127.0.0.1`, or any `localhost:*` port
- **Production**: `www.agroverse.shop`, `agroverse.shop`, or any `github.io` domain

## Configuration Files

### `js/config.js`
This file automatically detects the environment and sets:
- Base URL (localhost vs production domain)
- Google App Script URL (dev vs prod)
- Stripe mode (test vs live)

**You only need to update:**
```javascript
const GOOGLE_SCRIPT_URL = isLocal
  ? 'YOUR_LOCAL_DEV_SCRIPT_URL'  // ← Update this
  : 'YOUR_PRODUCTION_SCRIPT_URL'; // ← Update this
```

## Two Separate Google App Scripts (Recommended)

### Option 1: Separate Scripts (Recommended)
Create **two separate Google App Script projects**:

1. **Development Script**
   - Use Stripe **test** keys
   - Deploy and get Web App URL
   - Use this URL in `config.js` for `YOUR_LOCAL_DEV_SCRIPT_URL`

2. **Production Script**
   - Use Stripe **live** keys
   - Deploy and get Web App URL
   - Use this URL in `config.js` for `YOUR_PRODUCTION_SCRIPT_URL`

### Option 2: Single Script with Environment Detection
Use one script that detects environment from the request:

```javascript
// In Google App Script
const environment = data.environment || 'production';
const stripeKey = environment === 'development' 
  ? PropertiesService.getScriptProperties().getProperty('STRIPE_TEST_KEY')
  : PropertiesService.getScriptProperties().getProperty('STRIPE_LIVE_KEY');
```

## Stripe Configuration

### Development (Test Mode)
- Use Stripe **test** API keys
- Use Stripe **test** webhook secret
- Use Stripe **test** price IDs
- Test cards: `4242 4242 4242 4242`

### Production (Live Mode)
- Use Stripe **live** API keys
- Use Stripe **live** webhook secret
- Use Stripe **live** price IDs
- Real payment processing

## Google Sheets

You can use:
- **One sheet** for both environments (recommended for simplicity)
- **Separate sheets** for dev and prod (more isolation)

If using one sheet, consider adding an "Environment" column to distinguish test vs live orders.

## Testing Checklist

### Development Testing
- [ ] Local server running on `localhost:8000`
- [ ] `js/config.js` points to dev Google App Script URL
- [ ] Google App Script uses Stripe test keys
- [ ] Product pages have test Stripe Price IDs
- [ ] Cart works locally
- [ ] Checkout redirects to Stripe test mode
- [ ] Orders save to Google Sheet
- [ ] Order status page works

### Production Testing
- [ ] Site deployed to GitHub Pages
- [ ] `js/config.js` points to prod Google App Script URL
- [ ] Google App Script uses Stripe live keys
- [ ] Product pages have live Stripe Price IDs
- [ ] Cart works on production domain
- [ ] Checkout redirects to Stripe live mode
- [ ] Orders save to Google Sheet
- [ ] Order status page works

## Switching Between Environments

The system automatically switches based on hostname, so:

1. **For local development**: Just run `localhost:8000` - it will use dev config
2. **For production**: Deploy to GitHub Pages - it will use prod config

No code changes needed when switching!

## Environment Variables Summary

| Variable | Development | Production |
|----------|-------------|------------|
| Hostname | `localhost` | `www.agroverse.shop` |
| Base URL | `http://localhost:8000` | `https://www.agroverse.shop` |
| Stripe Mode | Test | Live |
| Stripe Keys | `sk_test_...` | `sk_live_...` |
| Google Script | Dev deployment URL | Prod deployment URL |
| Success URL | `localhost:8000/order-status` | `agroverse.shop/order-status` |

## Troubleshooting

### "Google App Script URL not configured"
- Check `js/config.js` - make sure URLs are set (not `YOUR_..._URL`)
- Verify the script is deployed as Web App

### Wrong Stripe mode
- Check which Stripe keys are in Google App Script Properties
- Verify you're using the correct Google App Script URL for your environment

### Orders going to wrong sheet
- If using separate sheets, verify Sheet ID in Script Properties matches your environment
- Check the sheet name matches (`Orders` by default)

