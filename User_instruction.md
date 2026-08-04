# Hindi Autocomplete Prototype

Welcome to the Hindi Autocomplete prototype! This tool works seamlessly with Google Docs to predict and type Hindi legal and police terminology.

## Prerequisites

- **Google Chrome** browser.
- **Python 3.8+** installed on your computer.

> [!CAUTION]
> **CRITICAL:** When installing Python, make sure to check the box that says **"Add Python to PATH"** at the bottom of the installer window.

## Step 1: Start the Backend Server

The Chrome extension needs a local "brain" to process predictions.

1. Open the folder containing this project.
2. Double-click the file named `start.bat`.
3. A black command prompt window will open. It will automatically install the required libraries and start the server.
   > **Note:** Leave this black window open while you are using the autocomplete!

## Step 2: Install the Chrome Extension

1. Open Google Chrome.
2. Type `chrome://extensions/` in the URL bar and press **Enter**.
3. In the top right corner, turn **ON** Developer mode.
4. In the top left, click the **Load unpacked** button.
5. Select the folder named `extension` (or whatever folder contains the `manifest.json` file) inside this project directory.
   
The extension is now installed!

## Step 3: How to Use

1. Open a Google Doc.
2. Press `Ctrl + Space` to activate the autocomplete (check the console/overlay).
3. Start typing in Hindi.
4. When the prediction overlay appears, use the **Up/Down Arrows** to select a word.
5. Press **Right Control (Ctrl)** to accept the prediction and let the system type it for you!
