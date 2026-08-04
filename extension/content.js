console.log("Content.js loaded");

let overlayX = 0;
let overlayY = 0;
let selectedPrediction = "";
let autocompleteEnabled = false;

(function () {
    const iframe = document.querySelector(".docs-texteventtarget-iframe");

    if (!iframe) {
        console.log("Typing iframe not found.");
        return;
    }

    const doc = iframe.contentDocument;
    console.log("Iframe found.");

    //------------------------------------------------
    // Timers & Constants for Real-Time Feel
    //------------------------------------------------
    let typingTimer = null;
    let overlayTimer = null;
    const DEBOUNCE_DELAY = 300; // Wait 400ms after user stops typing to fetch
    const OVERLAY_DURATION = 5000; // Hide overlay after 2 seconds

    //------------------------------------------------
    // Overlay
    //------------------------------------------------
    const overlay = document.createElement("div");
    overlay.id = "autocomplete-overlay";
    overlay.style.position = "fixed";
    overlay.style.display = "none";
    overlay.style.background = "#808080";
    overlay.style.border = "1px solid #cfcfcf";
    overlay.style.borderRadius = "6px";
    overlay.style.padding = "6px";
    overlay.style.boxShadow = "0 2px 10px rgba(0,0,0,0.2)";
    overlay.style.fontSize = "14px";
    overlay.style.fontFamily = "Arial";
    overlay.style.zIndex = "2147483647";

    document.body.appendChild(overlay);

    let selectedIndex = 0;
    let currentPredictions = [];

    //------------------------------------------------
    // Show Overlay
    //------------------------------------------------
    function showOverlay(predictions, x, y) {
        overlayX = x;
        overlayY = y;
        currentPredictions = predictions;
        selectedIndex = 0;

        renderOverlay();

        // 3. Auto-hide logic (Hide after 2 seconds)
        clearTimeout(overlayTimer);
        overlayTimer = setTimeout(() => {
            hideOverlay();
        }, OVERLAY_DURATION);
    }

    //------------------------------------------------
    // Render Overlay
    //------------------------------------------------
    function renderOverlay() {
        overlay.innerHTML = "";

        currentPredictions.forEach((text, index) => {
            const div = document.createElement("div");
            div.textContent = text;
            div.style.padding = "6px 10px";
            div.style.cursor = "pointer";

            if (index === selectedIndex) {
                div.style.background = "#2563eb";
                div.style.color = "white";
            }

            overlay.appendChild(div);
        });

        if (currentPredictions.length > 0) {
            selectedPrediction = currentPredictions[selectedIndex];
        }

        overlay.style.left = overlayX + "px";
        overlay.style.top = (overlayY + 20) + "px";
        overlay.style.display = "block";
    }

    function hideOverlay() {
        overlay.style.display = "none";
        currentPredictions = [];
        selectedPrediction = "";
        selectedIndex = 0;
        
        // Clear the hide timer if we are hiding it manually
        clearTimeout(overlayTimer); 
    }

    // ******************************
    // PREDICTION LOGIC
    // ******************************
    async function requestPrediction() {
        const cursor = document.querySelector(".kix-cursor");

        if (!cursor) {
            console.log("Cursor not found");
            return;
        }

        const rect = cursor.getBoundingClientRect();
        const cursorY = rect.top;

        const lines = [...document.querySelectorAll("rect[aria-label]")]
            .map(r => ({
                rect: r,
                text: r.getAttribute("aria-label"),
                top: r.getBoundingClientRect().top
            }))
            .sort((a, b) => a.top - b.top);

        if (lines.length === 0) return;

        let nearest = lines[0];

        for (const line of lines) {
            if (Math.abs(line.top - cursorY) < Math.abs(nearest.top - cursorY)) {
                nearest = line;
            }
        }

        const paragraph = nearest.rect.parentElement;
        const currentParagraph = [...paragraph.querySelectorAll("rect[aria-label]")]
            .map(r => r.getAttribute("aria-label"))
            .join(" ");

        let previousParagraph = "";
        let prev = paragraph.previousElementSibling;

        while (prev) {
            if (prev.tagName === "g" && prev.getAttribute("role") === "paragraph") {
                previousParagraph = [...prev.querySelectorAll("rect[aria-label]")]
                    .map(r => r.getAttribute("aria-label"))
                    .join(" ");
                break;
            }
            prev = prev.previousElementSibling;
        }

        const context = (previousParagraph + " " + currentParagraph).trim();

        try {
            console.log("Requesting prediction for context:", context);
            const response = await chrome.runtime.sendMessage({
                type: "PREDICT",
                text: context
            });

            if (response.success) {
                showOverlay(response.predictions, rect.left, rect.top);
            }
        } catch (err) {
            console.error(err);
        }
    }

    //------------------------------------------------
    // Continuous Typing Listener (Real-Time Updates)
    //------------------------------------------------
    doc.addEventListener("keyup", function (event) {
        if (!autocompleteEnabled) return;

        // Ignore navigation/control keys (we don't want to trigger fetches on them)
        const ignoredKeys = [
            "Shift", "Control", "Alt", "Meta", 
            "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", 
            "Tab", "Escape", "Enter"
        ];
        
        if (ignoredKeys.includes(event.key)) return;

        // 1. Immediately hide the stale overlay while the user is typing
        hideOverlay();

        // 2. Clear the previous timer so we don't spam the API on every single keystroke
        clearTimeout(typingTimer);

        // Set a new timer. If the user pauses for 400ms, fetch the new context!
        typingTimer = setTimeout(() => {
            requestPrediction();
        }, DEBOUNCE_DELAY);
    });

    //------------------------------------------------
    // Keyboard Listener (Overrides & Toggles)
    //------------------------------------------------
    doc.addEventListener("keydown", async function (event) {

        // Overlay Navigation
        if (overlay.style.display === "block") {
            if (event.key === "ArrowDown") {
                event.preventDefault();
                if (currentPredictions.length === 0) return;
                selectedIndex = (selectedIndex + 1) % currentPredictions.length;
                renderOverlay();
                return;
            }

            if (event.key === "ArrowUp") {
                event.preventDefault();
                if (currentPredictions.length === 0) return;
                selectedIndex--;
                if (selectedIndex < 0) selectedIndex = currentPredictions.length - 1;
                renderOverlay();
                return;
            }

            // Accept Prediction
            if (event.code === "ControlRight") {
                console.log("ControlRight intercepted");

                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();

                if (currentPredictions.length === 0) return;

                // Stop the typing timer so it doesn't fetch mid-acceptance
                clearTimeout(typingTimer); 

                chrome.runtime.sendMessage({
                    type: "SELECT",
                    text: currentPredictions[selectedIndex]
                }, () => {
                    hideOverlay();
                    if (!autocompleteEnabled) return;
                    
                    // Fetch the next prediction immediately after accepting
                    setTimeout(() => {
                        requestPrediction();
                    }, 200);
                });
                return;
            }

            if (event.key === "Escape") {
                event.preventDefault();
                hideOverlay();
                return;
            }
        }

        // Trigger Prediction Toggle
        if (event.ctrlKey && event.code === "Space") {
            event.preventDefault();
            autocompleteEnabled = !autocompleteEnabled;
            console.log("Autocomplete:", autocompleteEnabled);

            if (autocompleteEnabled) {
                requestPrediction();
            } else {
                hideOverlay();
                clearTimeout(typingTimer);
            }
            return;
        }
    },true);

    // Hide overlay when clicking outside
    document.addEventListener("mousedown", () => {
        if (overlay.style.display === "block") hideOverlay();
    });

})();