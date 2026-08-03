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

    selectedIndex = 0;

    }
    // ******************************
    // PREDICTION lOGIC
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

    if (lines.length === 0)
        return;

    let nearest = lines[0];

    for (const line of lines) {

        if (
            Math.abs(line.top - cursorY)
            <
            Math.abs(nearest.top - cursorY)
        ) {
            nearest = line;
        }

    }

    const paragraph = nearest.rect.parentElement;

    const currentParagraph =
        [...paragraph.querySelectorAll("rect[aria-label]")]
            .map(r => r.getAttribute("aria-label"))
            .join(" ");

    let previousParagraph = "";

    let prev = paragraph.previousElementSibling;

    while (prev) {

        if (
            prev.tagName === "g"
            &&
            prev.getAttribute("role") === "paragraph"
        ) {

            previousParagraph =
                [...prev.querySelectorAll("rect[aria-label]")]
                    .map(r => r.getAttribute("aria-label"))
                    .join(" ");

            break;
        }

        prev = prev.previousElementSibling;

    }

    const context =
        (previousParagraph + " " + currentParagraph).trim();

    try {

        const response =
            await chrome.runtime.sendMessage({

                type: "PREDICT",

                text: context

            });

        if (response.success) {

            showOverlay(
                response.predictions,
                rect.left,
                rect.top
            );

        }

    }
    catch (err) {

        console.error(err);

    }

    }

    
    //------------------------------------------------
    // Keyboard
    //------------------------------------------------

    doc.addEventListener("keydown", async function (event) {

        //--------------------------------------------
        // Overlay Navigation
        //--------------------------------------------

        if (overlay.style.display === "block") {

            if (event.key === "ArrowDown") {

                event.preventDefault();

                if (currentPredictions.length === 0)
                    return;

                selectedIndex =
                    (selectedIndex + 1) %
                    currentPredictions.length;

                renderOverlay();
                return;
            }

            if (event.key === "ArrowUp") {

                event.preventDefault();

                if (currentPredictions.length === 0)
                    return;

                selectedIndex--;

                if (selectedIndex < 0)
                    selectedIndex =
                        currentPredictions.length - 1;

                renderOverlay();
                return;
            }

            //----------------------------------------
            // Accept Prediction
            //----------------------------------------

            if (event.key === "Tab") {

                 event.preventDefault();
                 event.stopPropagation();
                 event.stopImmediatePropagation();

                if (currentPredictions.length === 0)
                    return;

                const selectedPrediction =
                    currentPredictions[selectedIndex];

               chrome.runtime.sendMessage({
                    type: "SELECT",
                    text: selectedPrediction
                });

                hideOverlay();

                return;

            }

            if (event.key === "Escape") {

                event.preventDefault();

                hideOverlay();

                return;

            }
        }

        //--------------------------------------------
        // Trigger Prediction
        //--------------------------------------------

        if (!(event.ctrlKey && event.code === "Space"))
            return;

        event.preventDefault();

        console.log("Ctrl + Space detected");

        //------------------------------------------------
        // Cursor
        //------------------------------------------------

        const cursor = document.querySelector(".kix-cursor");

        if (!cursor) {
            console.log("Cursor not found");
            return;
        }

        const rect = cursor.getBoundingClientRect();

        console.log("Cursor Position");
        console.log("left :", rect.left);
        console.log("top  :", rect.top);
        console.log("height :", rect.height);

        const cursorY = rect.top;

        //------------------------------------------------
        // Visible Lines
        //------------------------------------------------

        const lines = [...document.querySelectorAll("rect[aria-label]")]
            .map(r => ({
                rect: r,
                text: r.getAttribute("aria-label"),
                top: r.getBoundingClientRect().top
            }))
            .sort((a, b) => a.top - b.top);

        if (lines.length === 0) {
            console.log("No visible lines");
            return;
        }

        //------------------------------------------------
        // Nearest Line
        //------------------------------------------------

        let nearest = lines[0];

        for (const line of lines) {

            if (
                Math.abs(line.top - cursorY) <
                Math.abs(nearest.top - cursorY)
            ) {
                nearest = line;
            }
        }

        //------------------------------------------------
        // Current Paragraph
        //------------------------------------------------

        const paragraph = nearest.rect.parentElement;

        const currentParagraph =
            [...paragraph.querySelectorAll("rect[aria-label]")]
                .map(r => r.getAttribute("aria-label"))
                .join(" ");

        //------------------------------------------------
        // Previous Paragraph
        //------------------------------------------------

        let previousParagraph = "";

        let prev = paragraph.previousElementSibling;

        while (prev) {

            if (
                prev.tagName === "g" &&
                prev.getAttribute("role") === "paragraph"
            ) {

                previousParagraph =
                    [...prev.querySelectorAll("rect[aria-label]")]
                        .map(r => r.getAttribute("aria-label"))
                        .join(" ");

                break;
            }

            prev = prev.previousElementSibling;
        }

        //------------------------------------------------
        // Context
        //------------------------------------------------

        const context =
            (previousParagraph + " " + currentParagraph).trim();

        console.log("========== CONTEXT ==========");
        console.log(context);
        console.log("=============================");

        //------------------------------------------------
        // Prediction
        //------------------------------------------------

        try {

            const response =
                await chrome.runtime.sendMessage({

                    type: "PREDICT",
                    text: context

                });

            console.log(response);

            if (response.success) {

                console.log(response.predictions);

                showOverlay(
                    response.predictions,
                    rect.left,
                    rect.top
                );
            }

        }
        catch (err) {

            console.error(err);

        }

    });

    document.addEventListener("mousedown", () => {

    if (overlay.style.display === "block")
        hideOverlay();

});

})();