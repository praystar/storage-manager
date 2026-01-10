// Native Messaging version - uses native messaging instead of HTTP
// This file replaces popup.js when using native messaging

document.addEventListener("DOMContentLoaded", async () => {
    const { pendingDownload } = await chrome.storage.local.get("pendingDownload");
    
    if (!pendingDownload) {
        document.getElementById("diskInfo").innerHTML = '<div class="loading">No pending download.</div>';
        document.getElementById("confirm").disabled = true;
        document.getElementById("cancel").disabled = true;
        return;
    }

    // Clear badge when popup opens
    chrome.action.setBadgeText({ text: "" });

    const fileSizeMB = pendingDownload.fileSize > 0 ?
        (pendingDownload.fileSize / (1024 * 1024)).toFixed(2) :
        "Unknown";

    // Get the download directory path
    let downloadPath = "/";
    try {
        if (pendingDownload.filename) {
            // Extract directory from filename (e.g., /home/user/Downloads/file.txt -> /home/user/Downloads)
            const pathParts = pendingDownload.filename.split('/');
            if (pathParts.length > 1) {
                downloadPath = pathParts.slice(0, -1).join('/');
            } else {
                downloadPath = pendingDownload.filename.substring(0, pendingDownload.filename.lastIndexOf('/')) || "/";
            }
        }
    } catch (err) {
        console.log("Could not determine download path, using default:", err);
    }

    // Update file info
    const fileName = pendingDownload.filename || pendingDownload.url;
    const displayName = fileName.length > 50 ? fileName.substring(0, 50) + '...' : fileName;
    document.getElementById("fileName").textContent = displayName;
    document.getElementById("fileSize").textContent = fileSizeMB !== "Unknown" ? `${fileSizeMB} MB` : "Unknown";
    document.getElementById("filePath").textContent = downloadPath;

    document.getElementById("sizeInput").value =
        fileSizeMB !== "Unknown" ? fileSizeMB : "";

    // Load and display disk space information
    await loadDiskInfo(downloadPath);

    // Store downloadPath in closure for button handlers
    const storedDownloadPath = downloadPath;

    document.getElementById("confirm").onclick = async () => {
        const inputValue = parseFloat(document.getElementById("sizeInput").value);
        if (!inputValue || inputValue <= 0) {
            showError("Please enter a valid estimated size in MB.");
            return;
        }

        const sizeBytes = inputValue * 1024 * 1024;

        try {
            const data = await sendNativeMessage('check', {
                size: sizeBytes,
                path: storedDownloadPath
            });
            
            if (!data.ok) {
                showError(`Not enough space! ${data.error}`);
                try {
                    await chrome.downloads.cancel(pendingDownload.id);
                } catch (err) {
                    console.error("Error canceling download:", err);
                }
            } else {
                try {
                    await chrome.downloads.resume(pendingDownload.id);
                    // Refresh disk info to show updated space
                    await loadDiskInfo(storedDownloadPath);
                    // Close after a brief delay to show updated info
                    setTimeout(() => {
                        chrome.storage.local.remove("pendingDownload");
                        window.close();
                    }, 1000);
                } catch (err) {
                    console.error("Error resuming download:", err);
                    showError("Could not resume download. Please check manually.");
                }
            }
        } catch (err) {
            console.error("Error checking space:", err);
            showError("Failed to contact native host. Make sure the native host is installed correctly.");
            try {
                await chrome.downloads.cancel(pendingDownload.id);
            } catch (cancelErr) {
                console.error("Error canceling download:", cancelErr);
            }
            setTimeout(() => {
                chrome.storage.local.remove("pendingDownload");
                window.close();
            }, 2000);
        }
    };

    document.getElementById("cancel").onclick = async () => {
        try {
            await chrome.downloads.cancel(pendingDownload.id);
        } catch (err) {
            console.error("Error canceling download:", err);
        }
        await chrome.storage.local.remove("pendingDownload");
        window.close();
    };
});

async function loadDiskInfo(path) {
    const diskInfoDiv = document.getElementById("diskInfo");
    diskInfoDiv.innerHTML = '<div class="loading">Loading disk space...</div>';

    try {
        const data = await sendNativeMessage('info', { path: path });
        
        if (!data.ok) {
            throw new Error(data.error || "Failed to get disk info");
        }

        // Calculate percentage used
        const percentUsed = data.percent_used;
        const percentFree = 100 - percentUsed;
        
        // Determine bar color based on free space
        let barClass = "high";
        if (percentFree < 10) {
            barClass = "low";
        } else if (percentFree < 25) {
            barClass = "medium";
        }

        diskInfoDiv.innerHTML = `
            <div class="disk-info-header">
                <div class="disk-info-title">💾 Available Disk Space</div>
            </div>
            <div class="disk-info-path" title="${data.path}">${data.path}</div>
            <div class="disk-space-display">
                <div class="free-space-label">Free Space</div>
                <div class="free-space">${data.free_gb} GB</div>
                <div class="space-bar-container">
                    <div class="space-bar ${barClass}" style="width: ${percentFree}%">
                        ${percentFree.toFixed(1)}%
                    </div>
                </div>
                <div class="space-stats">
                    <span>Used: ${data.used_gb} GB</span>
                    <span>Total: ${data.total_gb} GB</span>
                </div>
            </div>
        `;
    } catch (err) {
        console.error("Error loading disk info:", err);
        diskInfoDiv.innerHTML = `
            <div class="loading" style="color: #e53e3e;">
                ⚠️ Could not load disk space info.<br>
                <small>Make sure native host is installed</small>
            </div>
        `;
    }
}

function sendNativeMessage(command, params = {}) {
    return new Promise((resolve, reject) => {
        const message = {
            command: command,
            ...params
        };

        chrome.runtime.sendNativeMessage('com.storage_checker', message, (response) => {
            if (chrome.runtime.lastError) {
                reject(new Error(chrome.runtime.lastError.message || 'Native host connection failed'));
                return;
            }
            
            if (!response) {
                reject(new Error('No response from native host'));
                return;
            }
            
            if (response.ok === false) {
                reject(new Error(response.error || 'Unknown error'));
            } else {
                resolve(response);
            }
        });
    });
}

function showError(message) {
    const errorDiv = document.getElementById("errorMessage");
    errorDiv.textContent = message;
    errorDiv.classList.add("show");
    setTimeout(() => {
        errorDiv.classList.remove("show");
    }, 5000);
}

