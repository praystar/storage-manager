# Native Messaging Implementation

This document describes the native messaging alternative to the Flask server.

## Quick Start

1. **Install native host:**
   ```bash
   ./install_native_host.sh <your-extension-id>
   ```

2. **Switch extension to native messaging:**
   ```bash
   cd my_extension
   cp popup.js popup_flask.js  # Backup
   cp ../popup_native.js popup.js  # Use native version
   cp manifest.json manifest_flask.json  # Backup
   cp manifest_native.json manifest.json  # Use native manifest
   ```

3. **Reload extension** in Chrome

4. **Done!** No server needed - the native host runs on-demand.

## How It Works

### Native Messaging Protocol

1. Extension sends JSON message via `chrome.runtime.sendNativeMessage()`
2. Chrome launches the native host process (`native_host.py`)
3. Native host reads message from stdin (4-byte length + JSON)
4. Native host processes the request
5. Native host writes response to stdout (4-byte length + JSON)
6. Native host exits
7. Extension receives the response

### Message Format

**Request:**
```json
{
  "command": "info",
  "path": "/home/user/Downloads"
}
```

**Response:**
```json
{
  "ok": true,
  "path": "/home/user/Downloads",
  "total": 500000000000,
  "used": 400000000000,
  "free": 100000000000,
  "percent_used": 80.0,
  "total_gb": 465.66,
  "used_gb": 372.53,
  "free_gb": 93.13
}
```

### Commands

- `info`: Get disk space information
- `check`: Check if there's enough space for a download
- `ping`: Health check

## Files

- `native_host.py`: Native messaging host script
- `com.storage_checker.json`: Native messaging manifest template
- `install_native_host.sh`: Installation script
- `popup_native.js`: Extension popup using native messaging
- `manifest_native.json`: Extension manifest for native messaging

## Benefits

✅ **No Background Process**: Only runs when needed  
✅ **Lower Resource Usage**: Zero memory/CPU when idle  
✅ **Faster**: No server startup time  
✅ **Simpler**: No port management, firewall issues  
✅ **Production Ready**: Native messaging is designed for production use  

## See Also

- [NATIVE_MESSAGING_SETUP.md](./NATIVE_MESSAGING_SETUP.md) - Detailed setup guide
- [README.md](./README.md) - Main documentation

