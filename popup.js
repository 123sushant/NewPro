document.addEventListener('DOMContentLoaded', async () => {
    const currentUrlSpan = document.getElementById('current-url');
    const checkBtn = document.getElementById('check-btn');
    const resultDiv = document.getElementById('result');
    const predictionText = document.getElementById('prediction');
    const errorText = document.getElementById('error');

    let currentTabUrl = '';

    // Reset UI
    resultDiv.classList.add('hidden');
    errorText.classList.add('hidden');

    // Fetch the active tab URL
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];
        if (currentTab && currentTab.url) {
            currentTabUrl = currentTab.url;
            currentUrlSpan.textContent = currentTabUrl;
        } else {
            currentUrlSpan.textContent = "Unable to detect URL.";
            checkBtn.disabled = true;
        }
    });

    checkBtn.addEventListener('click', async () => {
        if (!currentTabUrl) {
            errorText.textContent = "No URL available to check.";
            errorText.classList.remove('hidden');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: currentTabUrl })
            });

            if (!response.ok) {
                throw new Error("Failed to fetch prediction.");
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            predictionText.textContent = data.prediction;
            resultDiv.classList.remove('hidden');
        } catch (error) {
            errorText.textContent = error.message;
            errorText.classList.remove('hidden');
        }
    });
});
