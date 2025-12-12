# Testing Guide for Disk Space Checker Extension

## Step 1: Start the Flask Server

Open a terminal and run:

```bash
source venv/bin/activate
python3 local_app.py
```

You should see:
```
[YYYY-MM-DD HH:MM:SS][hostname] 🚀 Starting local disk monitor on port 5000...
 * Running on http://127.0.0.1:5000
```

**Keep this terminal open** - the server needs to keep running.

## Step 2: Load the Extension in Your Browser

### For Chrome:
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Navigate to and select: `/home/prayash/Documents/storage-manager/my_extension`
5. The extension should appear in your extensions list

### For Edge:
1. Open Edge and go to `edge://extensions/`
2. Enable "Developer mode" (toggle in bottom-left)
3. Click "Load unpacked"
4. Navigate to and select: `/home/prayash/Documents/storage-manager/my_extension`

## Step 3: Test the Extension

### Test 1: Basic Download Test
1. Find a file to download (any size will work)
2. Click the download link
3. The download should **pause automatically**
4. The extension popup should open (or you'll see a badge notification)
5. Check the file size shown in the popup
6. Click "✅ Confirm" to check space and resume, or "❌ Cancel" to cancel

### Test 2: Test with Known File Size
1. Download a file with a known size (e.g., a small image or document)
2. Verify the popup shows the correct file size
3. Confirm the download

### Test 3: Test with Unknown File Size
1. Try downloading a file where the size isn't known
2. Enter an estimated size in MB in the input field
3. Confirm the download

### Test 4: Test Server Connection
1. Stop the Flask server (Ctrl+C in the terminal)
2. Try to download a file
3. You should see an error: "Failed to contact local server"
4. Restart the server and try again

## Step 4: Check the Server Logs

Watch the terminal where Flask is running. You should see logs like:
```
[2024-12-13 00:00:00][hostname] Checked path: /home/prayash/Downloads
[2024-12-13 00:00:00][hostname] Total space: 500.00 GB
[2024-12-13 00:00:00][hostname] Free space: 100.00 GB
[2024-12-13 00:00:00][hostname] Requested download size: 0.50 GB
[2024-12-13 00:00:00][hostname] Enough space. Free: 100.00 GB
```

## Troubleshooting

### Extension doesn't pause downloads
- Check browser console (F12 → Console tab) for errors
- Verify `background.js` is loaded (check extension details page)
- Make sure you have the "downloads" permission

### Popup doesn't open automatically
- Click the extension icon manually
- Check if there's a badge notification (red "!" on the icon)

### "Failed to contact local server" error
- Make sure Flask server is running on port 5000
- Check if port 5000 is already in use: `lsof -i :5000`
- Try accessing `http://localhost:5000/check?size=1000000` in your browser

### Extension shows "No pending download"
- This is normal if no download was started
- Start a download first, then open the popup

## Quick Test Command

Test the Flask API directly:

curl "http://localhost:5000/check?size=1000000000&path="


This should return JSON with disk space information.

