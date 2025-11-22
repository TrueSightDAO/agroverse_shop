# Local Development Setup

## Quick Start

The easiest way to run the site locally is using one of the provided scripts:

### Option 1: Use the Startup Script (Recommended)

**macOS/Linux:**
```bash
chmod +x start-local-server.sh
./start-local-server.sh
```

**Windows:**
```cmd
start-local-server.bat
```

The script will automatically:
- Detect if Node.js or Python is installed
- Install dependencies if needed
- Start a local server on `http://127.0.0.1:8000`

### Option 2: Using npm (Node.js)

If you have Node.js installed:

```bash
# Install dependencies (first time only)
npm install

# Start server
npm run dev
# or
npm start
```

This will start a server on `http://127.0.0.1:8000`

### Option 3: Using Python

**Python 3:**
```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

**Python 2:**
```bash
python -m SimpleHTTPServer 8000
```

Then visit: `http://127.0.0.1:8000`

### Option 4: VS Code Live Server Extension

1. Install the "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

**Note:** Make sure to configure it to use `127.0.0.1` instead of `localhost` if needed.

---

## Why 127.0.0.1 instead of file://?

Opening files directly with `file://` protocol has limitations:
- ❌ CORS restrictions (Google Places API, fetch requests won't work)
- ❌ localStorage may have restrictions
- ❌ Some browser APIs require HTTP/HTTPS
- ❌ No proper MIME types

Using `http://127.0.0.1:8000` provides:
- ✅ Full HTTP protocol support
- ✅ CORS works properly
- ✅ All browser APIs function correctly
- ✅ Proper MIME types for files
- ✅ Matches production environment better

---

## Port Configuration

The default port is **8000**. If you need to change it:

1. **Update `js/config.js`:**
   ```javascript
   const baseUrl = isLocal 
     ? 'http://127.0.0.1:YOUR_PORT'  // Change this
     : 'https://www.agroverse.shop';
   ```

2. **Update server command:**
   ```bash
   # Node.js
   http-server -p YOUR_PORT -a 127.0.0.1
   
   # Python
   python3 -m http.server YOUR_PORT --bind 127.0.0.1
   ```

---

## Troubleshooting

### "Port 8000 already in use"
Use a different port:
```bash
# Node.js
http-server -p 8001 -a 127.0.0.1

# Python
python3 -m http.server 8001 --bind 127.0.0.1
```

Don't forget to update `js/config.js` with the new port!

### "Cannot find module http-server"
Install dependencies:
```bash
npm install
```

### "Permission denied" (macOS/Linux)
Make the script executable:
```bash
chmod +x start-local-server.sh
```

### Google Places API not working
- Make sure you're using `http://127.0.0.1:8000` (not `file://`)
- Check browser console for CORS errors
- Verify your API key allows `127.0.0.1` as an origin

---

## Environment Detection

The system automatically detects local development when:
- Hostname is `127.0.0.1` or `localhost`
- Port is any number (8000, 8001, etc.)

This triggers:
- Development Google App Script URL
- Test Stripe keys
- Development base URLs

No code changes needed when switching between local and production!

---

## Recommended Setup

1. **Use the startup script** for convenience
2. **Keep port 8000** unless you have conflicts
3. **Bookmark** `http://127.0.0.1:8000` in your browser
4. **Use browser DevTools** to debug (F12)

---

## Next Steps

Once your local server is running:
1. Visit `http://127.0.0.1:8000`
2. Test the cart functionality
3. Test checkout flow (with Stripe test mode)
4. Verify order status page

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for complete setup instructions.

