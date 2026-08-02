console.log("Overlay JS loaded");
window.test123 = "overlay is alive";
let suggestionBox = null;

function createSuggestionBox() {
    if (suggestionBox) return suggestionBox;

    suggestionBox = document.createElement("div");

    suggestionBox.id = "autocomplete-suggestion";

    suggestionBox.style.position = "fixed";
    suggestionBox.style.pointerEvents = "none";

    suggestionBox.style.color = "#999";
    suggestionBox.style.fontSize = "14px";
    suggestionBox.style.fontFamily = "Arial";

    suggestionBox.style.whiteSpace = "pre";

    suggestionBox.style.zIndex = "999999";

    suggestionBox.style.opacity = "0.8";

    document.body.appendChild(suggestionBox);

    return suggestionBox;
}

function showSuggestion(x, y, text) {

    createSuggestionBox();

    suggestionBox.textContent = text;

    suggestionBox.style.left = x + "px";
    suggestionBox.style.top = y + "px";

    suggestionBox.style.display = "block";
}

function hideSuggestion() {

    if (suggestionBox)
        suggestionBox.style.display = "none";
}

// showSuggestion(300, 300, "Hello");










// console.log("Overlay JS loaded successfully");

// let suggestionBox = null;

// function createSuggestionBox() {
//     if (suggestionBox) return suggestionBox;

//     suggestionBox = document.createElement("div");
//     suggestionBox.id = "hindi-autocomplete-suggestion";

//     // CSS Styling for absolute maximum visibility
//     suggestionBox.style.position = "fixed";
//     suggestionBox.style.pointerEvents = "none"; // Lets you click "through" the box
    
//     // TEMPORARY DEBUG STYLING: Yellow background, red border, big black text
//     suggestionBox.style.backgroundColor = "rgba(255, 255, 0, 0.8)"; 
//     suggestionBox.style.border = "2px solid red";
//     suggestionBox.style.color = "#000000"; 
    
//     suggestionBox.style.fontSize = "18px"; 
//     suggestionBox.style.fontFamily = "Arial, sans-serif";
//     suggestionBox.style.whiteSpace = "pre";
    
//     // 2147483647 is the maximum possible z-index in CSS. 
//     // This forces it above EVERYTHING in Google Docs.
//     suggestionBox.style.zIndex = "2147483647"; 
//     suggestionBox.style.padding = "2px 5px";

//     document.body.appendChild(suggestionBox);
//     console.log("Suggestion box created and added to document.body");

//     return suggestionBox;
// }

// // We attach it to 'window' so you can call it from the console
// window.showSuggestion = function(x, y, text) {
//     console.log(`showSuggestion triggered: x=${x}, y=${y}, text=${text}`);
//     createSuggestionBox();

//     suggestionBox.textContent = text;
//     suggestionBox.style.left = x + "px";
//     suggestionBox.style.top = y + "px";
//     suggestionBox.style.display = "block";
// };

// window.hideSuggestion = function() {
//     if (suggestionBox) {
//         suggestionBox.style.display = "none";
//     }
// };

// // Fire a test immediately when the script loads
// window.showSuggestion(300, 300, "Initial Test Loaded!");