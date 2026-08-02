console.log("Content.js loaded");

(function () {

    const iframe = document.querySelector(".docs-texteventtarget-iframe");

    if (!iframe) {
        console.log("Typing iframe not found.");
        return;
    }

    const doc = iframe.contentDocument;

    console.log("Iframe found.");

    // --------------------------------------------------
    // Debug all typing events
    // --------------------------------------------------

    const events = [
        "keydown",
        "keypress",
        "keyup",
        "beforeinput",
        "input",
        "compositionstart",
        "compositionupdate",
        "compositionend",
        "textInput",
        "paste"
    ];

    events.forEach(type => {

        doc.addEventListener(type, e => {

            console.log(
                "EVENT:",
                type,
                e.constructor.name,
                e
            );

        }, true);

    });

    // --------------------------------------------------
    // Ctrl + Space
    // --------------------------------------------------

    doc.addEventListener("keydown", async function (event) {

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

        const cursorY = cursor.getBoundingClientRect().top;

        //------------------------------------------------
        // Visible lines
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
        // Nearest line
        //------------------------------------------------

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

        //------------------------------------------------
        // Paragraph
        //------------------------------------------------

        const paragraph = nearest.rect.parentElement;

        const currentParagraph = [...paragraph.querySelectorAll("rect[aria-label]")]
            .map(r => r.getAttribute("aria-label"))
            .join(" ");

        //------------------------------------------------
        // Previous paragraph
        //------------------------------------------------

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

        //------------------------------------------------
        // Final Context
        //------------------------------------------------

        const context = (
            previousParagraph +
            " " +
            currentParagraph
        ).trim();

        console.log("========== CONTEXT ==========");
        console.log(context);
        console.log("=============================");

        //------------------------------------------------
        // Ask background for prediction
        //------------------------------------------------

        try {

            const response = await chrome.runtime.sendMessage({

                type: "PREDICT",

                text: context

            });

            console.log(response);

            if (response.success) {
            console.log(response.predictions);

            await navigator.clipboard.writeText(
            response.predictions[0]
            );
            }

        }

        catch (err) {

            console.error(err);

        }

    });

})();