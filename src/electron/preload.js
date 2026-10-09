const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('desktop', {
  backendConfig: () => ipcRenderer.invoke('app:backendConfig'),
  selectFolder: () => ipcRenderer.invoke('dialog:selectFolder'),
  selectMediaFiles: () => ipcRenderer.invoke('dialog:selectMediaFiles'),
  selectAudioFile: () => ipcRenderer.invoke('dialog:selectAudioFile'),
  selectVideoFile: () => ipcRenderer.invoke('dialog:selectVideoFile'),
  fileUrl: value => ipcRenderer.invoke('file:toUrl', value),
  openPath: value => ipcRenderer.invoke('shell:openPath', value),
  openExternal: value => ipcRenderer.invoke('shell:openExternal', value),
  getSecret: key => ipcRenderer.invoke('secret:get', key),
  setSecret: (key, value) => ipcRenderer.invoke('secret:set', key, value),
  setAutoStart: enabled => ipcRenderer.invoke('settings:autoStart', enabled),
  setMinimizeToTray: enabled => ipcRenderer.invoke('settings:minimizeToTray', enabled),
  onLog: callback => {
    const listener = (_, value) => callback(value)
    ipcRenderer.on('desktop:log', listener)
    return () => ipcRenderer.removeListener('desktop:log', listener)
  },
})

