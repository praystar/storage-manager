chrome.downloads.onCreated.addListener(async (item) => {
    console.log("Download started:", item);

    try {
        // Pause the download immediately - simple approach like Flask version
        await chrome.downloads.pause(item.id);
        console.log("Download paused successfully:", item.id);

        // Save it for the popup to handle
        await chrome.storage.local.set({ pendingDownload: item });

        // Open the popup automatically
        try {
            await chrome.action.openPopup();
        } catch (err) {
            // Popup might not open if user already has it open or if browser doesn't allow it
            // In that case, show a notification or badge
            console.log("Could not auto-open popup:", err);
            chrome.action.setBadgeText({ text: "!" });
            chrome.action.setBadgeBackgroundColor({ color: "#f44336" });
        }
    } catch (error) {
        // Handle "must be in progress" error gracefully - this happens when download
        // completes or is interrupted before we can pause it
        const errorMsg = error.message || error.toString() || String(error);
        if (errorMsg.includes('must be in progress') || errorMsg.includes('Download must be in progress')) {
            console.log("Download not in progress (completed or interrupted), skipping");
            return;
        }
        
        // For other errors, log but don't cancel
        console.error("Error pausing download:", error);
    }
});
