chrome.runtime.onInstalled.addListener(() => {
    console.log("Fraud Website Detection extension installed.");
});

// Add a context menu for checking the current tab's URL
chrome.contextMenus.create({
    id: "checkURL",
    title: "Check Current Tab URL for Fraud",
    contexts: ["all"]
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "checkURL") {
        const currentTab = tab;
        if (currentTab && currentTab.url) {
            try {
                const response = await fetch('http://127.0.0.1:5000/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: currentTab.url })
                });

                const data = await response.json();
                if (data.error) {
                    console.error(data.error);
                    alert(`Error: ${data.error}`);
                } else {
                    alert(`Prediction: ${data.prediction}`);
                }
            } catch (error) {
                console.error(error);
                alert("An error occurred while fetching the prediction.");
            }
        } else {
            alert("No valid URL found for this tab.");
        }
    }
});
