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
    
    console.log('=== READ GENERATE QUEUE ===');
    const queuePath = path.join(__dirname, '..', 'training-queue.json');
    
    console.log('Reading from:', queuePath);
    
    if (!fs.existsSync(queuePath)) {
      return { success: false, error: 'Training queue not found' };
    }
    
    const content = fs.readFileSync(queuePath, 'utf-8');
    const queue = JSON.parse(content);
    
    console.log('Queue generate:', queue.generate);
    
    return { 
      success: true, 
      generateConfigs: queue.generate || []  // This is the key difference!
    };
  } catch (error) {
    console.error('Error reading generate queue:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-image-data', async (event, name, prompt, imageName) => {
  try {
    const imagePath = path.join(
      __dirname,
      '..',
      'server',
      'app_backend',
      'generate',
      'output',
      name,
      prompt,
      imageName
    );
    
    console.log('Loading image from:', imagePath);
    
    if (!fs.existsSync(imagePath)) {
      console.error('Image not found at:', imagePath);
      return { success: false, error: 'Image not found' };
    }
    
    // Read image as base64
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');
    const ext = path.extname(imagePath).toLowerCase();
    
    // Determine MIME type
    let mimeType = 'image/jpeg';
    if (ext === '.png') mimeType = 'image/png';
    else if (ext === '.bmp') mimeType = 'image/bmp';
    else if (ext === '.gif') mimeType = 'image/gif';
    
    const dataUrl = `data:${mimeType};base64,${base64Image}`;
    
    return { success: true, dataUrl };
  } catch (error) {
    console.error('Error loading image:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('count-generated-images', async (event, name, prompt) => {
  try {
    const outputPath = path.join(
      __dirname, 
      '..', 
      'server', 
      'app_backend', 
      'generate', 
      'output', 
      name, 
      prompt
    );
    
    console.log('Checking for images at:', outputPath);
    
    if (!fs.existsSync(outputPath)) {
      return { success: true, count: 0, imageNames: [] };
    }
    
    const files = fs.readdirSync(outputPath);
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif'];
    const imageNames = files.filter(file => {
      const ext = path.extname(file).toLowerCase();
      return imageExtensions.includes(ext);
    });
    
    console.log('Images found:', imageNames.length);
    
    return { 
      success: true, 
      count: imageNames.length,
      imageNames: imageNames  // Return just the names
    };
  } catch (error) {
    console.error('Error counting images:', error);
    return { success: false, error: error.message, count: 0, imageNames: [] };
  }
});

ipcMain.handle('get-image-path', async (event, name, prompt, imageName) => {
  try {
    const imagePath = path.join(
      __dirname,
      '..',
      'server',
      'app_backend',
      'generate',
      'output',
      name,
      prompt,
      imageName
    );
    
    if (!fs.existsSync(imagePath)) {
      return { success: false, error: 'Image not found' };
    }
    
    return { success: true, path: imagePath };
  } catch (error) {
    return { success: false, error: error.message };
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