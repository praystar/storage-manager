chrome.downloads.onCreated.addListener(async (item) => {
    console.log("Download started:", item);

    try {
        // Pause the download immediately - this is critical!
        // The pause happens asynchronously, but Chrome will pause it very quickly
        await chrome.downloads.pause(item.id);
        console.log("✅ Download paused successfully:", item.id);

        // Verify the download is actually paused
        const downloadItem = await chrome.downloads.search({ id: item.id });
        if (downloadItem.length > 0 && downloadItem[0].state === 'in_progress') {
            // If still in progress, try pausing again (race condition protection)
            console.log("Download still in progress, pausing again...");
            await chrome.downloads.pause(item.id);
        }

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
        console.error("❌ Error pausing download:", error);
        // If we can't pause, cancel it to be safe
        try {
            await chrome.downloads.cancel(item.id);
            console.log("Download canceled due to pause failure");
        } catch (cancelError) {
            console.error("Error canceling download:", cancelError);
        }
    }
});
