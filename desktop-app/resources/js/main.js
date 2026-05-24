// This is just a sample app. You can structure your Neutralinojs app code as you wish.
// This example app is written with vanilla JavaScript and HTML.
// Feel free to use any frontend framework you like :)
// See more details: https://neutralino.js.org/docs/how-to/use-a-frontend-library

/*
    Function to display information about the Neutralino app.
    This function updates the content of the 'info' element in the HTML
    with details regarding the running Neutralino application, including
    its ID, port, operating system, and version information.
*/
function showInfo() {
  return `
        ${NL_APPID} is running on port ${NL_PORT} inside ${NL_OS}
        <br/><br/>
        <span>server: v${NL_VERSION} . client: v${NL_CVERSION}</span>
        `;
}

/*
    Function to open the official Neutralino documentation in the default web browser.
*/
function openDocs() {
  Neutralino.os.open("https://neutralino.js.org/docs");
}

/*
    Function to open a tutorial video on Neutralino's official YouTube channel in the default web browser.
*/
function openTutorial() {
  Neutralino.os.open("https://www.youtube.com/c/CodeZri");
}

/*
    Function to set up a system tray menu with options specific to the window mode.
    This function checks if the application is running in window mode, and if so,
    it defines the tray menu items and sets up the tray accordingly.
*/
function setTray() {
  // Tray menu is only available in window mode
  if (typeof NL_MODE === "undefined" || NL_MODE != "window") {
    console.log("INFO: Tray menu is only available in the window mode.");
    return;
  }

  // Define tray menu items
  let tray = {
    icon: "/resources/assets/icon.jpg",
    menuItems: [
      { id: "VERSION", text: "Get version" },
      { id: "SEP", text: "-" },
      { id: "QUIT", text: "Quit" },
    ],
  };

  // Set the tray menu
  try {
    Neutralino.os.setTray(tray);
  } catch (e) {
    console.warn("Failed to set system tray:", e);
  }
}

/*
    Function to handle click events on the tray menu items.
    This function performs different actions based on the clicked item's ID,
    such as displaying version information or exiting the application.
*/
function onTrayMenuItemClicked(event) {
  switch (event.detail.id) {
    case "VERSION":
      // Display version information
      Neutralino.os.showMessageBox(
        "Version information",
        `Neutralinojs server: v${NL_VERSION} | Neutralinojs client: v${NL_CVERSION}`,
      );
      break;
    case "QUIT":
      // Exit the application
      Neutralino.app.exit();
      break;
  }
}

/*
    Function to handle the window close event by gracefully exiting the Neutralino application.
*/
function onWindowClose() {
  Neutralino.app.exit();
}

// Initialize Neutralino if in native environment
if (typeof Neutralino !== 'undefined') {
  Neutralino.init();

  // Register event listeners
  Neutralino.events.on("trayMenuItemClicked", onTrayMenuItemClicked);
  Neutralino.events.on("windowClose", onWindowClose);

  // Conditional initialization: Set up system tray if not running on macOS
  if (typeof NL_OS !== 'undefined' && NL_OS != "Darwin") {
    // TODO: Fix https://github.com/neutralinojs/neutralinojs/issues/615
    setTray();
  }
}

// Open file passed as command-line argument (e.g. when double-clicking a .md file)
(async function loadInitialFile() {
  if (typeof Neutralino === 'undefined' || typeof NL_ARGS === 'undefined') return;
  const args = Array.isArray(NL_ARGS) ? NL_ARGS : (() => { try { return JSON.parse(NL_ARGS); } catch(e) { return []; } })();
  const filePath = args.find(a => typeof a === 'string' && /\.(md|markdown)$/i.test(a));
  if (!filePath) return;

  try {
    const content = await Neutralino.filesystem.readFile(filePath);
    const fileName = filePath.split(/[/\\]/).pop().replace(/\.(md|markdown)$/i, '');
    
    window.NL_INITIAL_FILE_CONTENT = {
      name: fileName,
      content: content
    };

    // Callback hook in case script.js loaded first
    if (window.NL_IMPORT_EXTERNAL_FILE) {
      window.NL_IMPORT_EXTERNAL_FILE(content, fileName);
    }
  } catch (e) {
    console.warn('Could not open initial file:', e);
  }
})();
