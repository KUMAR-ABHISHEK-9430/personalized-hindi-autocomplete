chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

    if (message.type !== "PREDICT") {
        return;
    }

    fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            text: message.text,
        }),
    })
        .then((response) => response.json())
        .then((data) => {

            sendResponse({
                success: true,
                predictions: data.predictions,
            });

        })
        .catch((error) => {

            console.error(error);

            sendResponse({
                success: false,
                predictions: [],
            });

        });

    // Keep the message channel open while fetch() finishes.
    return true;

});