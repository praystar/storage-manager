# Disk Space Checker - Browser Extension

A Chrome/Edge browser extension for Linux users that automatically pauses downloads and checks available disk space before allowing them to proceed. This helps prevent running out of storage space during large downloads.

## Features

- 🛑 **Automatic Download Pausing**: Automatically pauses all downloads when they start
- 💾 **Real-time Disk Space Display**: Shows available disk space with visual progress bar
- ✅ **Smart Space Checking**: Verifies sufficient space before resuming downloads
- 🎨 **Modern UI**: Beautiful, intuitive interface with color-coded space indicators
- 🔒 **Safety Buffer**: Maintains a configurable reserved space buffer (default: 5GB)

## Screenshots

The extension popup displays:
- Current available disk space with visual progress bar
- File information (name, size, download path)
- Color-coded space indicators (green/orange/red)
- Easy confirm/cancel buttons

## Architecture

The extension consists of two main components:

1. **Browser Extension** (`my_extension/`): Chrome/Edge extension that intercepts downloads
2. **Backend** (choose one):
   - **Flask Server** (`local_app.py`): HTTP server that runs continuously
   - **Native Messaging Host** (`native_host.py`): On-demand process (recommended)

### Communication Methods

**Option 1: Flask Server (Original)**
- Extension communicates via HTTP (`http://localhost:5000`)
- Server runs continuously in background
- Requires Flask dependency
- See [README.md](./README.md) for setup

**Option 2: Native Messaging (Recommended)**
- Extension communicates via native messaging protocol
- Host only runs when needed (on-demand)
- More efficient, no background process
- See [NATIVE_MESSAGING_SETUP.md](./NATIVE_MESSAGING_SETUP.md) for setup

## Installation

### Prerequisites

- Linux operating system
- Python 3.8+ with pip
- Chrome or Edge browser

### Step 1: Install Python Dependencies

```bash
cd /path/to/storage-manager
python3 -m venv venv
source venv/bin/activate
pip install flask psutil
```

### Step 2: Load the Extension

1. Open Chrome/Edge and navigate to:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`

2. Enable **Developer mode** (toggle in top-right corner)

3. Click **"Load unpacked"**

4. Select the `my_extension` folder from this repository

5. The extension should now appear in your extensions list

### Step 3: Choose Backend Method

#### Option A: Native Messaging (Recommended - More Efficient)

1. **Install the native messaging host:**
   ```bash
   ./install_native_host.sh <your-extension-id>
   ```
   Get your extension ID from `chrome://extensions/` (enable Developer mode)

2. **Switch extension to native messaging:**
   ```bash
   cd my_extension
   cp popup.js popup_flask.js  # Backup Flask version
   cp ../popup_native.js popup.js  # Use native version
   cp manifest.json manifest_flask.json  # Backup
   cp manifest_native.json manifest.json  # Use native manifest
   ```

3. **Reload the extension** in Chrome

**No server needed!** The native host runs on-demand.

See [NATIVE_MESSAGING_SETUP.md](./NATIVE_MESSAGING_SETUP.md) for detailed instructions.

#### Option B: Flask Server (Original Method)

1. **Start the Flask server:**
   ```bash
   ./start_server.sh
   ```
   Or manually:
   ```bash
   source venv/bin/activate
   python3 local_app.py
   ```

2. **Keep the terminal open** - the server must be running

You should see:
```
Starting local disk monitor on port 5000...
 * Running on http://127.0.0.1:5000
```

## Usage

1. **Set up your chosen backend** (see Step 3 above)
   - Native Messaging: Install native host (one-time setup)
   - Flask Server: Start the server (must be running)

2. **Download a file** from any website

3. The download will **automatically pause** and the extension popup will open

4. **Review the information**:
   - Check your available disk space at the top
   - Review file name, size, and download path
   - Enter estimated size if unknown

5. **Make a decision**:
   - Click **"Confirm"** to check space and resume download (if enough space)
   - Click **"Cancel"** to cancel the download

6. The extension will:
   - Check available space against the file size + reserved buffer
   - Resume download if sufficient space
   - Cancel download if insufficient space

## Configuration

### Configuration

#### Native Messaging Host

Edit `native_host.py` to customize:

```python
DEFAULT_MIN_SIZE = 1 * 1024**3          # 1 GB assumed if unknown
RESERVED_SPACE = 5 * 1024**3            # Always keep 5 GB free
```

#### Flask Server

Edit `local_app.py` to customize:

```python
DEFAULT_MIN_SIZE = 1 * 1024**3          # 1 GB assumed if unknown
RESERVED_SPACE = 5 * 1024**3            # Always keep 5 GB free
PORT = 5000                              # Server port
```

### Extension Settings

The extension automatically detects the download directory from the file path. If detection fails, it defaults to checking the home directory.

## Testing

### Quick Test

1. Start the Flask server
2. Test the API directly:
   ```bash
   curl "http://localhost:5000/info?path=/home/user/Downloads"
   ```
3. Try downloading a small file
4. Verify the popup appears and shows disk space

### Comprehensive Testing

See [TESTING.md](./TESTING.md) for detailed testing procedures and test cases.

## Known Issues & Limitations

For a detailed list of known issues, limitations, and planned improvements, see [KNOWN_ISSUES.md](./KNOWN_ISSUES.md).

**Quick Summary:**
- ⚠️ **Multiple Downloads**: Only handles one download at a time
- ⚠️ **Path Detection**: May not always detect correct download directory
- ⚠️ **Server Dependency**: Requires Flask server to be running
- ⚠️ **Platform Support**: Currently Linux-only

See [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) for detailed information, workarounds, and proposed solutions.

## Production Deployment

### ⚠️ Important: Flask Development Server Warning

The current Flask server uses the **development server** (`app.run()`), which is **NOT suitable for production**. The Flask development server:
- Is single-threaded
- Has security vulnerabilities
- Is not optimized for performance
- Should only be used for development

### Recommended Production Solutions

#### Option 1: Gunicorn (Recommended for Linux)

**Installation:**
```bash
pip install gunicorn
```

**Run with Gunicorn:**
```bash
gunicorn -w 2 -b 127.0.0.1:5000 local_app:app
```

**With systemd service** (create `/etc/systemd/system/storage-checker.service`):
```ini
[Unit]
Description=Storage Checker Flask App
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/storage-manager
Environment="PATH=/path/to/storage-manager/venv/bin"
ExecStart=/path/to/storage-manager/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 local_app:app

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable storage-checker
sudo systemctl start storage-checker
```

#### Option 2: uWSGI

**Installation:**
```bash
pip install uwsgi
```

**Run with uWSGI:**
```bash
uwsgi --http 127.0.0.1:5000 --wsgi-file local_app.py --callable app --processes 2 --threads 2
```

#### Option 3: Waitress (Cross-platform, Simple)

**Installation:**
```bash
pip install waitress
```

**Modify `local_app.py`:**
```python
from waitress import serve

if __name__ == "__main__":
    log(f"🚀 Starting local disk monitor on port {PORT}...")
    serve(app, host='127.0.0.1', port=PORT)
```

**Run:**
```bash
python3 local_app.py
```

#### Option 4: Docker (Containerized)

**Create `Dockerfile`:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY local_app.py .

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "local_app:app"]
```

**Create `requirements.txt`:**
```
flask>=3.0.0
psutil>=7.0.0
gunicorn>=21.0.0
```

**Build and run:**
```bash
docker build -t storage-checker .
docker run -d -p 5000:5000 --name storage-checker storage-checker
```

### Security Considerations for Production

1. **Firewall**: Only allow localhost connections (127.0.0.1), not 0.0.0.0
2. **Authentication**: Consider adding API key authentication
3. **HTTPS**: For remote access, use a reverse proxy (nginx) with SSL
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Logging**: Set up proper logging and monitoring
6. **Error Handling**: Improve error handling and user feedback

### Example Production Setup with Nginx (if needed for remote access)

```nginx
server {
    listen 5000;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Development

### Project Structure

```
storage-manager/
├── my_extension/          # Browser extension files
│   ├── manifest.json      # Extension manifest
│   ├── background.js      # Service worker (download interceptor)
│   ├── popup.html         # Popup UI
│   ├── popup.js           # Popup logic
│   ├── style.css          # Popup styling
│   └── icon.png           # Extension icon
├── native_host.py           # native messaging 
├── native_host.sh        # Set up native messaging
├── 
├── README.md              # This file (main documentation)
├── 
└── KNOWN_ISSUES.md        # Known issues and limitations
```

### API Endpoints

#### `GET /info?path=<path>`
Get current disk space information.=

**Parameters:**
- `path` (optional): Directory path to check (default: `/`)

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

#### `GET /check?size=<bytes>&path=<path>`
Check if there's enough space for a download.

**Parameters:**
- `size` (required): File size in bytes
- `path` (optional): Directory path to check (default: `/`)

**Response (success):**
```json
{
  "ok": true,
  "total": 500000000000,
  "used": 400000000000,
  "free": 100000000000,
  "reserved": 5368709120
}
```

**Response (insufficient space):**
```json
{
  "ok": false,
  "error": "Not enough space. Free: 93.13 GB, Required: 100.00 GB",
  "total": 500000000000,
  "used": 400000000000,
  "free": 100000000000,
  "reserved": 5368709120
}
```

## Troubleshooting

### Extension doesn't pause downloads
- Check browser console (F12 → Console) for errors
- Verify extension has "downloads" permission
- Check if background service worker is running


### Popup doesn't open automatically
- Click the extension icon manually
- Look for red "!" badge notification
- Check browser console for errors

### Wrong disk space shown
- Verify the download path is correct
- Check if path exists and is accessible
- Ensure you have read permissions for the path



## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Areas for Contribution

- Multiple download queue support
- Cross-platform compatibility (Windows, macOS)
- Settings page for configuration
- Server health monitoring
- Better error handling
- Unit tests
- Documentation improvements
