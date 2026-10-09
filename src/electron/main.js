const { app, BrowserWindow, Menu, Tray, dialog, ipcMain, nativeImage, safeStorage, session, shell } = require('electron')
const { spawn } = require('child_process')
const { randomBytes } = require('crypto')
const fs = require('fs')
const net = require('net')
const path = require('path')
const { pathToFileURL } = require('url')

const APP_TITLE = '实体店新媒体AI智能体社区版'
app.setName('StorefrontMediaAgentCommunity')
app.setPath('userData', path.join(app.getPath('appData'), 'StorefrontMediaAgentCommunity'))
const PROJECT_ROOT = path.resolve(__dirname, '..', '..')
const DEV_URL = 'http://127.0.0.1:5173'
const API_TOKEN = randomBytes(32).toString('hex')
const ALLOWED_PLATFORM_HOSTS = new Set(['creator.douyin.com', 'channels.weixin.qq.com', 'cp.kuaishou.com', 'creator.xiaohongshu.com'])
let mainWindow
let tray
let backendProcess
let backendPort = 35107
let forceQuit = false
let minimizeToTray = true

if (!app.requestSingleInstanceLock()) app.quit()
app.setName(APP_TITLE)
if (process.platform === 'win32') app.setAppUserModelId('cn.storefront.mediaagent')

function userDataFile(name) { return path.join(app.getPath('userData'), name) }
function log(message) {
  const line = `${new Date().toISOString()} ${message}\n`
  try { fs.mkdirSync(app.getPath('logs'), { recursive: true }); fs.appendFileSync(path.join(app.getPath('logs'), 'desktop.log'), line, 'utf8') } catch {}
  if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send('desktop:log', line.trim())
}
function iconPath() {
  const candidates = app.isPackaged
    ? [path.join(process.resourcesPath, 'assets', 'app-icon.png')]
    : [path.join(PROJECT_ROOT, 'assets', 'app-icon.png')]
  return candidates.find(fs.existsSync) || ''
}
function appIcon(size = 256) {
  const candidate = iconPath()
  if (!candidate) return nativeImage.createEmpty()
  const image = nativeImage.createFromPath(candidate)
  return image.isEmpty() ? image : image.resize({ width: size, height: size })
}
function findPort(start = 35107, attempts = 20) {
  return new Promise((resolve, reject) => {
    const tryPort = (port, remaining) => {
      const server = net.createServer()
      server.unref()
      server.once('error', () => remaining > 0 ? tryPort(port + 1, remaining - 1) : reject(new Error('没有可用的本地端口')))
      server.listen(port, '127.0.0.1', () => server.close(() => resolve(port)))
    }
    tryPort(start, attempts)
  })
}
async function waitForBackend(timeoutMs = 25000) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${backendPort}/api/health`)
      if (response.ok) return true
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 350))
  }
  return false
}
async function startBackend() {
  backendPort = await findPort()
  const dataDir = path.join(app.getPath('userData'), 'data')
  const outputDir = path.join(app.getPath('videos'), APP_TITLE)
  fs.mkdirSync(dataDir, { recursive: true })
  fs.mkdirSync(outputDir, { recursive: true })
  const env = {
    ...process.env,
    STOREX_BACKEND_PORT: String(backendPort),
    STOREX_DATA_DIR: dataDir,
    STOREX_OUTPUT_DIR: outputDir,
    STOREX_API_TOKEN: API_TOKEN,
  }
  if (app.isPackaged) env.STOREX_FFMPEG_DIR = path.join(process.resourcesPath, 'ffmpeg')
  let executable
  let args
  let cwd
  if (app.isPackaged) {
    executable = path.join(process.resourcesPath, 'backend', 'backend.exe')
    args = []
    cwd = path.dirname(executable)
  } else {
    const venvPython = path.join(PROJECT_ROOT, '.venv', 'Scripts', 'python.exe')
    executable = fs.existsSync(venvPython) ? venvPython : 'python'
    args = [path.join(PROJECT_ROOT, 'src', 'backend', 'main.py')]
    cwd = path.join(PROJECT_ROOT, 'src', 'backend')
    env.STOREX_LICENSE_PUBLIC_KEY = path.join(cwd, 'license_public.pem')
  }
  if (app.isPackaged && !fs.existsSync(executable)) throw new Error(`后端程序缺失：${executable}`)
  backendProcess = spawn(executable, args, { cwd, env, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] })
  backendProcess.stdout.on('data', data => log(`[backend] ${data.toString().trim()}`))
  backendProcess.stderr.on('data', data => log(`[backend] ${data.toString().trim()}`))
  backendProcess.once('exit', code => { log(`后端退出，代码 ${code}`); backendProcess = null })
  if (!(await waitForBackend())) throw new Error('本地视频引擎启动超时，请查看日志')
  log(`后端已启动：http://127.0.0.1:${backendPort}`)
}
function stopBackend() {
  if (!backendProcess) return
  try { backendProcess.kill() } catch {}
  backendProcess = null
}
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440, height: 920, minWidth: 1100, minHeight: 720,
    title: APP_TITLE, icon: appIcon(), backgroundColor: '#07101b', show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  })
  mainWindow.removeMenu()
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }))
  mainWindow.webContents.on('will-navigate', event => event.preventDefault())
  if (app.isPackaged) mainWindow.loadFile(path.join(PROJECT_ROOT, 'src', 'frontend', 'dist', 'index.html'))
  else mainWindow.loadURL(DEV_URL)
  mainWindow.once('ready-to-show', () => mainWindow.show())
  mainWindow.on('close', event => {
    if (!forceQuit && minimizeToTray) { event.preventDefault(); mainWindow.hide() }
  })
}
function createTray() {
  const image = appIcon(16)
  if (image.isEmpty()) return
  tray = new Tray(image)
  tray.setToolTip(APP_TITLE)
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: '显示工作台', click: () => { mainWindow.show(); mainWindow.focus() } },
    { type: 'separator' },
    { label: '退出', click: () => { forceQuit = true; app.quit() } },
  ]))
  tray.on('double-click', () => { mainWindow.show(); mainWindow.focus() })
}
function readSecrets() {
  try { return JSON.parse(fs.readFileSync(userDataFile('secure-secrets.json'), 'utf8')) } catch { return {} }
}
function writeSecrets(payload) { fs.writeFileSync(userDataFile('secure-secrets.json'), JSON.stringify(payload), 'utf8') }

ipcMain.handle('app:backendConfig', () => ({ url: `http://127.0.0.1:${backendPort}`, token: API_TOKEN }))
ipcMain.handle('dialog:selectFolder', async () => { const result = await dialog.showOpenDialog(mainWindow, { properties: ['openDirectory', 'createDirectory'] }); return result.canceled ? '' : result.filePaths[0] })
ipcMain.handle('dialog:selectMediaFiles', async () => { const result = await dialog.showOpenDialog(mainWindow, { properties: ['openFile', 'multiSelections'], filters: [{ name: '视频与图片', extensions: ['mp4','mov','avi','mkv','webm','m4v','jpg','jpeg','png','webp','bmp'] }] }); return result.canceled ? [] : result.filePaths })
ipcMain.handle('dialog:selectAudioFile', async () => { const result = await dialog.showOpenDialog(mainWindow, { properties: ['openFile'], filters: [{ name: '音乐', extensions: ['mp3','wav','m4a','aac','flac'] }] }); return result.canceled ? '' : result.filePaths[0] })
ipcMain.handle('dialog:selectVideoFile', async () => { const result = await dialog.showOpenDialog(mainWindow, { properties: ['openFile'], filters: [{ name: '视频', extensions: ['mp4','mov','mkv','webm'] }] }); return result.canceled ? '' : result.filePaths[0] })
ipcMain.handle('file:toUrl', (_, value) => fs.existsSync(value) ? pathToFileURL(path.resolve(value)).href : '')
ipcMain.handle('shell:openPath', (_, value) => fs.existsSync(value) ? shell.openPath(path.resolve(value)) : '文件不存在')
ipcMain.handle('shell:openExternal', (_, value) => { const url = new URL(value); if (url.protocol !== 'https:' || !ALLOWED_PLATFORM_HOSTS.has(url.hostname)) throw new Error('不允许打开该网址'); return shell.openExternal(url.toString()) })
ipcMain.handle('secret:get', (_, key) => { if (!safeStorage.isEncryptionAvailable()) return ''; const value = readSecrets()[key]; if (!value) return ''; try { return safeStorage.decryptString(Buffer.from(value, 'base64')) } catch { return '' } })
ipcMain.handle('secret:set', (_, key, value) => { if (!safeStorage.isEncryptionAvailable()) throw new Error('系统安全存储不可用'); const secrets = readSecrets(); if (value) secrets[key] = safeStorage.encryptString(String(value)).toString('base64'); else delete secrets[key]; writeSecrets(secrets); return true })
ipcMain.handle('settings:autoStart', (_, enabled) => { app.setLoginItemSettings({ openAtLogin: Boolean(enabled), path: process.execPath }); return true })
ipcMain.handle('settings:minimizeToTray', (_, enabled) => { minimizeToTray = Boolean(enabled); return true })

app.on('second-instance', () => { if (mainWindow) { mainWindow.show(); mainWindow.focus() } })
app.whenReady().then(async () => {
  try {
    session.defaultSession.setPermissionCheckHandler(() => false)
    session.defaultSession.setPermissionRequestHandler((_, __, callback) => callback(false))
    await startBackend(); createWindow(); createTray()
  }
  catch (error) { log(error.stack || error.message); dialog.showErrorBox('启动失败', error.message); forceQuit = true; app.quit() }
})
app.on('before-quit', () => { forceQuit = true; stopBackend() })
app.on('window-all-closed', () => { if (process.platform !== 'darwin' && !minimizeToTray) app.quit() })
