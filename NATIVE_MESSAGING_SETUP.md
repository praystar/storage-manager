# Native Messaging Setup Guide

This guide explains how to set up the native messaging alternative, which is more efficient than the Flask server because it only runs when needed.

## Advantages of Native Messaging

✅ **On-Demand Execution**: The native host only runs when the extension needs it  
✅ **No Background Process**: No need to keep a server running  
✅ **Lower Resource Usage**: No constant memory/CPU usage  
✅ **Faster Startup**: No server startup time  
✅ **Better Integration**: Direct communication with the browser  

## Installation

### Step 1: Install Python Dependencies

```bash
cd /path/to/storage-manager
python3 -m venv venv
source venv/bin/activate
pip install psutil
```

Note: Flask is **not required** for native messaging!

### Step 2: Install Native Messaging Host

Run the installation script:

```bash
./install_native_host.sh
```

Or manually:

1. Make the native host executable:
   ```bash
   chmod +x native_host.py
   ```

2. Get your extension ID:
   - Go to `chrome://extensions/`
   - Enable Developer mode
   - Find your extension and copy its ID

3. Create the manifest directory:
   ```bash
   mkdir -p ~/.config/google-chrome/NativeMessagingHosts
   ```

4. Create the manifest file at `~/.config/google-chrome/NativeMessagingHosts/com.storage_checker.json`:
   ```json
   {
     "name": "com.storage_checker",
     "description": "Native messaging host for Disk Space Checker extension",
     "path": "/absolute/path/to/storage-manager/native_host.py",
     "type": "stdio",
     "allowed_origins": [
       "chrome-extension://YOUR_EXTENSION_ID_HERE/"
     ]
   }
   ```

   **Important**: 
   - Replace `/absolute/path/to/storage-manager/` with the actual absolute path
   - Replace `YOUR_EXTENSION_ID_HERE` with your extension ID

### Step 3: Update Extension to Use Native Messaging

1. **Replace `popup.js` with the native messaging version:**
   ```bash
   cd my_extension
   cp popup.js popup_flask.js  # Backup Flask version
   cp ../popup_native.js popup.js  # Use native version
   ```

   Or manually copy the contents of `popup_native.js` to `popup.js`.

2. **Update `manifest.json`:**
   - Remove `host_permissions` for localhost
   - Add `"nativeMessaging"` to permissions
   - Or use the provided `manifest_native.json`:
     ```bash
     cp manifest.json manifest_flask.json  # Backup
     cp manifest_native.json manifest.json  # Use native version
     ```

3. **Reload the extension** in Chrome:
   - Go to `chrome://extensions/`
   - Click the reload icon on your extension

## Testing

1. **Test the native host directly:**
   ```bash
   echo '{"command":"ping"}' | python3 native_host.py
   ```
   Should return: `{"ok":true,"message":"pong"}`

2. **Test with the extension:**
   - Start a download
   - The popup should appear and show disk space
   - No Flask server needed!

## Troubleshooting

### "Native host not found" error

- Check that the manifest file exists in the correct location
- Verify the path in the manifest is absolute and correct
- Ensure `native_host.py` is executable: `chmod +x native_host.py`
- Check that the extension ID in the manifest matches your actual extension ID

### "Permission denied" error

- Make sure `native_host.py` is executable: `chmod +x native_host.py`
- Check file permissions on the manifest directory

### Extension ID changes after reload

- If you reload the extension in developer mode, the ID may change
- Update the extension ID in the manifest file
- Or use a permanent extension ID (pack the extension)

### Testing native host manually

You can test the native host with a simple script:

```python
import json
import struct
import sys

# Send a test message
message = {"command": "info", "path": "/"}
message_json = json.dumps(message)
message_bytes = message_json.encode('utf-8')
length = struct.pack('=I', len(message_bytes))
sys.stdout.buffer.write(length + message_bytes)
sys.stdout.buffer.flush()

# Read response
length_bytes = sys.stdin.buffer.read(4)
length = struct.unpack('=I', length_bytes)[0]
response_bytes = sys.stdin.buffer.read(length)
response = json.loads(response_bytes.decode('utf-8'))
print(json.dumps(response, indent=2))
```

Run: `python3 test_native.py < native_host.py`

## Switching Between Flask and Native Messaging

### To use Flask (original):
1. Use `popup.js` (Flask version)
2. Use `manifest.json` with `host_permissions`
3. Start Flask server: `./start_server.sh`

### To use Native Messaging:
1. Use `popup_native.js` (copy to `popup.js`)
2. Use `manifest_native.json` (copy to `manifest.json`)
3. Install native host: `./install_native_host.sh`
4. No server needed!

## File Locations

**Chrome:**
- `~/.config/google-chrome/NativeMessagingHosts/com.storage_checker.json`

**Chromium:**
- `~/.config/chromium/NativeMessagingHosts/com.storage_checker.json`

**Edge (Linux):**
- `~/.config/microsoft-edge/NativeMessagingHosts/com.storage_checker.json`

**Snap Chromium:**
- `~/snap/chromium/common/.config/chromium/NativeMessagingHosts/com.storage_checker.json`

## Uninstallation

To remove the native messaging host:

```bash
rm ~/.config/google-chrome/NativeMessagingHosts/com.storage_checker.json
rm ~/.config/chromium/NativeMessagingHosts/com.storage_checker.json
rm ~/.config/microsoft-edge/NativeMessagingHosts/com.storage_checker.json
```

## Comparison: Flask vs Native Messaging

| Feature | Flask Server | Native Messaging |
|---------|-------------|------------------|
| **Always Running** | Yes (background) | No (on-demand) |
| **Memory Usage** | ~50-100 MB | 0 MB (when idle) |
| **CPU Usage** | Minimal (idle) | 0% (when idle) |
| **Startup Time** | Server must start | Instant |
| **Setup Complexity** | Simple | Medium |
| **Dependencies** | Flask + psutil | psutil only |
| **Port Required** | Yes (5000) | No |
| **Firewall Issues** | Possible | None |
| **Production Ready** | Needs Gunicorn | Yes (native) |

## Recommendation

**Use Native Messaging** for:
- Personal use
- Better resource efficiency
- Simpler deployment (no server management)

**Use Flask** for:
- Development/testing
- Remote access (with proper security)
- Multiple users/instances

