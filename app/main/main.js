const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
require('electron-reload')(__dirname);

ipcMain.handle('read-training-queue', async () => {
  try {
    const queuePath = path.join(__dirname, "..", "training-queue.json");

    if (!fs.existsSync(queuePath)) {
      return {success: false, error: 'Training queue not found'};
    }

    const content = fs.readFileSync(queuePath, 'utf-8');
    const queue = JSON.parse(content);

    return {
      success: true,
      totalClasses: queue.train? queue.train.length : 0
    };

  } catch(error) {
    return {success: false, error: error.message};
  }
});


ipcMain.handle('read-training-log', async () => {
  try {
    const logPath = path.join(__dirname, '..', 'server', 'app_backend', 'train', 'train.log');
    
    if (!fs.existsSync(logPath)) {
      return { success: false, error: 'File not found' };
    }
    
    const content = fs.readFileSync(logPath, 'utf-8');
    
    if (!content || content.trim() === '') {
      return { success: false, error: 'File is empty' };
    }
    
    return { success: true, content };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('clear-training-log', async() => {
  try {
    const logPath = path.join(__dirname, '..', 'server', 'app_backend', 'train', 'train.log');
    fs.writeFileSync(logPath, '', 'utf-8');
    console.log('Training log cleared');
    return {success: true};
  } catch (error) {
    return {success: false, error: error.message};
  }
});

ipcMain.handle('read-generate-queue', async () => {
  try {
    const queuePath = path.join(__dirname, "..", "training-queue.json");

    if (!fs.existsSync(queuePath)) {
      return {success: false, error: 'Generate queue not found'};
    }

    const content = fs.readFileSync(queuePath, 'utf-8');
    const queue = JSON.parse(content);

    return {
      success: true,
      totalClasses: queue.generate? queue.generate.length : 0
    };

  } catch(error) {
    return {success: false, error: error.message};
  }
});


ipcMain.handle('read-generate-log', async () => {
  try {
    const logPath = path.join(__dirname, '..', 'server', 'app_backend', 'generate', 'generate.log');
    
    if (!fs.existsSync(logPath)) {
      return { success: false, error: 'File not found' };
    }
    
    const content = fs.readFileSync(logPath, 'utf-8');
    
    if (!content || content.trim() === '') {
      return { success: false, error: 'File is empty' };
    }
    
    return { success: true, content };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('clear-generate-log', async() => {
  try {
    const logPath = path.join(__dirname, '..', 'server', 'app_backend', 'generate', 'generate.log');
    fs.writeFileSync(logPath, '', 'utf-8');
    console.log('Generate log cleared');
    return {success: true};
  } catch (error) {
    return {success: false, error: error.message};
  }
});

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