# Known Issues & Future Improvements

This document tracks known issues, limitations, and planned improvements for the Disk Space Checker extension.

## Critical Issues

### None Currently

No critical issues that prevent basic functionality.

## Known Limitations

### 1. Multiple Simultaneous Downloads ⚠️

**Status**: Known Limitation  
**Priority**: Medium  
**Severity**: Medium

**Description**:  
The extension currently handles only one pending download at a time. When multiple downloads are started in quick succession, only the most recent download is tracked and paused.

**Current Behavior**:
- First download: Paused and tracked ✓
- Second download (before first is confirmed): Pauses and replaces first download in tracking
- First download: May continue or be lost

**Impact**:
- Users cannot queue multiple downloads
- Earlier downloads may not be properly managed
- Confusion when multiple downloads are started

**Workaround**:
- Wait for each download to be confirmed/canceled before starting another
- Use browser's download manager for multiple downloads

**Proposed Solution**:
```javascript
// Implement download queue
const downloadQueue = [];

chrome.downloads.onCreated.addListener(async (item) => {
    await chrome.downloads.pause(item.id);
    downloadQueue.push(item);
    await chrome.storage.local.set({ 
        pendingDownloads: downloadQueue 
    });
    // Show queue in popup
});
```

**Estimated Effort**: 4-6 hours

---

### 2. Download Path Detection Accuracy

**Status**: Known Limitation  
**Priority**: Medium  
**Severity**: Low

**Description**:  
Chrome's download API doesn't directly expose the configured download directory. The extension extracts the path from the filename, which may not always be accurate, especially for:
- Files downloaded to custom locations
- Files with relative paths
- Files on different partitions/mounts

**Current Behavior**:
- Extracts directory from `item.filename`
- Falls back to `/` if extraction fails
- May check wrong disk/partition

**Impact**:
- May show incorrect available space
- Could allow downloads when target disk is full
- Could block downloads when space is actually available

**Workaround**:
- Manually verify the download path shown in popup
- Use absolute paths in browser download settings

**Proposed Solution**:
1. Add settings page to configure default download directory
2. Use Chrome's `downloads.search()` to get more accurate path info
3. Allow user to override path in popup
4. Detect mount points and check correct partition

**Estimated Effort**: 6-8 hours

---

### 3. Small Download Window (Race Condition)

**Status**: Known Limitation  
**Priority**: Low  
**Severity**: Very Low

**Description**:  
There's a very small time window (milliseconds) between when a download starts and when the pause command takes effect. During this window, a small amount of data (typically <1KB) may download.

**Current Behavior**:
- Download starts → `onCreated` fires → Pause command sent
- ~10-50ms delay before pause takes effect
- 1-10KB may download (depending on connection speed)

**Impact**:
- Minimal - typically less than 1KB
- No practical impact on disk space checking

**Workaround**: None needed

**Proposed Solution**:  
This is a limitation of the Chrome API. No practical solution exists, but the impact is negligible.

**Estimated Effort**: N/A (API limitation)

---

### 4. Flask Server Dependency

**Status**: Known Limitation  
**Priority**: High  
**Severity**: Medium

**Description**:  
The extension requires a local Flask server to be running. If the server is not running, all downloads are canceled, which is frustrating for users.

**Current Behavior**:
- Extension tries to contact server
- If server is down: Download is canceled
- No automatic server startup
- No server status indicator

**Impact**:
- Poor user experience if server isn't running
- Downloads fail silently
- Users must remember to start server

**Workaround**:
- Always start server before browsing
- Use systemd service for auto-start (see README)
- Add server to startup applications

**Proposed Solutions**:

1. **Server Status Indicator** (Quick fix)
   - Add visual indicator in extension popup
   - Show "Server offline" warning
   - Estimated Effort: 2-3 hours

2. **Auto-start Server** (Medium complexity)
   - Detect if server is down
   - Attempt to start server automatically
   - Requires native messaging or external script
   - Estimated Effort: 8-10 hours

3. **Health Check Endpoint** (Easy)
   - Add `/health` endpoint
   - Extension pings on startup
   - Show status in popup
   - Estimated Effort: 1 hour

4. **Native Messaging** (Complex)
   - Replace Flask with native binary
   - Auto-starts with browser
   - Better integration
   - Estimated Effort: 20+ hours

**Recommended**: Implement solutions 1 and 3 first (health check + status indicator)

---

### 5. Popup Auto-Open Limitation

**Status**: Known Limitation  
**Priority**: Low  
**Severity**: Low

**Description**:  
Chrome/Edge security policies may prevent the popup from opening automatically. The `chrome.action.openPopup()` API only works in specific contexts and may fail silently.

**Current Behavior**:
- Extension tries to auto-open popup
- If it fails: Shows red "!" badge
- User must manually click extension icon

**Impact**:
- Users may not notice paused download
- Downloads may timeout if left paused too long
- Confusing user experience

**Workaround**:
- Look for red "!" badge on extension icon
- Manually click extension icon

**Proposed Solutions**:

1. **Browser Notifications** (Recommended)
   - Use `chrome.notifications` API
   - Show notification when download is paused
   - Click notification to open popup
   - Estimated Effort: 2-3 hours

2. **Persistent Badge** (Quick fix)
   - Keep badge visible until download is handled
   - Add badge text with download count
   - Estimated Effort: 1 hour

3. **Download Page Integration** (Complex)
   - Inject UI into chrome://downloads page
   - Show pending downloads there
   - Estimated Effort: 10+ hours

**Recommended**: Implement solution 1 (notifications)

---

### 6. Windows/macOS Compatibility

**Status**: Not Supported  
**Priority**: Low  
**Severity**: Low

**Description**:  
The extension is currently designed and tested only for Linux systems. The Flask backend uses Linux-specific path handling and may not work correctly on Windows or macOS.

**Current Behavior**:
- Works on Linux ✓
- Untested on Windows/macOS
- Path handling may fail on other OS

**Impact**:
- Cannot be used on Windows/macOS
- Limited user base

**Proposed Solution**:
1. Test on Windows/macOS
2. Fix path handling for cross-platform
3. Update documentation
4. Add OS detection
5. Handle different path formats

**Estimated Effort**: 8-12 hours

---

## Feature Requests

### High Priority

1. **Settings Page**
   - Configure default download directory
   - Adjust reserved space buffer
   - Set server port/address
   - Enable/disable auto-pause

2. **Download Queue Management**
   - Handle multiple pending downloads
   - Queue interface in popup
   - Batch confirm/cancel

3. **Server Health Monitoring**
   - Visual server status indicator
   - Auto-retry on connection failure
   - Health check endpoint

### Medium Priority

1. **Better Error Messages**
   - More descriptive error text
   - Actionable suggestions
   - Help links

2. **Download History**
   - Track checked downloads
   - Show space saved
   - Statistics

3. **Customizable UI**
   - Theme options
   - Size units (GB/MB/TB)
   - Color scheme

### Low Priority

1. **Export/Import Settings**
2. **Keyboard Shortcuts**
3. **Dark Mode**
4. **Multiple Language Support**

---

## Technical Debt

1. **Error Handling**: Improve error handling throughout codebase
2. **Testing**: Add unit tests and integration tests
3. **Code Documentation**: Add JSDoc/Python docstrings
4. **Type Safety**: Consider TypeScript for extension
5. **Logging**: Implement proper logging system
6. **Configuration**: Move hardcoded values to config file

---

## Security Considerations

1. **API Authentication**: Consider adding API key for local server
2. **Input Validation**: Validate all user inputs
3. **Path Traversal**: Prevent path traversal attacks
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **CORS**: Restrict CORS to localhost only in production

---

## Performance Optimizations

1. **Caching**: Cache disk space info (with TTL)
2. **Lazy Loading**: Load disk info only when needed
3. **Debouncing**: Debounce rapid download events
4. **Connection Pooling**: Reuse HTTP connections

---

## Documentation Needs

1. **API Documentation**: Detailed API endpoint docs
2. **Architecture Diagram**: Visual system architecture
3. **Contributing Guide**: How to contribute
4. **Troubleshooting Guide**: Common problems and solutions
5. **Video Tutorial**: Step-by-step setup video

---

## Future Enhancements

1. **Cloud Storage Integration**: Check cloud storage space
2. **Network Drive Support**: Check mounted network drives
3. **Smart Scheduling**: Schedule large downloads for off-peak hours
4. **Space Prediction**: Predict when disk will be full
5. **Cleanup Suggestions**: Suggest files to delete

---



