const { app, BrowserWindow } = require('electron');
const path = require('path');
require('electron-reload')(__dirname);

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 600,
    frame: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  //win.loadFile('./main/index.html'); // Load your HTML file
  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:5173') // React dev server
  } else {
    win.loadFile(path.join(__dirname, '../renderer/dist/index.html'))
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});