// app.js
const arialData = require('/fonts/arial.js');
const arialBoldData = require('/fonts/arialbd.js');

App({
  onLaunch() {
    wx.loadFontFace({
      global: true,
      family: 'Arial',
      source: `url("${arialData}")`,
      success: () => console.log('Arial 常规体加载成功')
    });
    wx.loadFontFace({
      global: true,
      family: 'Arial-Bold',
      source: `url("${arialBoldData}")`,
      success: () => console.log('Arial 粗体加载成功')
    });
  }
})
