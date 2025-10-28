const { app, BrowserWindow } = require("electron");
const path = require("path");
const url = require("url");

let win;

function createWindow() {
  win = new BrowserWindow({ width: 800, height: 600, icon: __dirname +  '/build/irius_favicon.png'});

  // load the dist folder from Angular
  win.loadURL(
    url.format({
      pathname: path.join(__dirname, '/build/index.html'),
      protocol: "file:",
      slashes: true
    })
  );
  const iconUrl = url.format({
    pathname: path.join(__dirname, '/build/irius_favicon.png'),
    protocol: 'file:',
    slashes: true
   })
  win.setMenuBarVisibility(false);
  win.maximize();

  // The following is optional and will open the DevTools:
  // win.webContents.openDevTools()

  win.on("closed", () => {
    win = null;
  });
}

app.on("ready", createWindow);

// on macOS, closing the window doesn't quit the app
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// initialize the app's main window
app.on("activate", () => {
  if (win === null) {
    createWindow();
  }
});