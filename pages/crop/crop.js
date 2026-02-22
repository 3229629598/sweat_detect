// pages/crop/crop.js
import WeCropper from '../../miniprogram_npm/we-cropper/index.js'

Page({
  data: {
    src: '', // 待裁剪图片地址
    cropperOpt: {
      id: 'cropper',
    }
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 接收上一页传递的 imageUrl 参数（解码）
    const imageUrl = decodeURIComponent(options.imageUrl);
    if (!imageUrl) {
      wx.showToast({title: '未获取到图片', icon: 'none'});
      wx.navigateBack(); // 无参数则返回上一页
      return;
    };
    // 定义裁剪区域尺寸
    const windowInfo = wx.getWindowInfo()
    const width = windowInfo.windowWidth
    const height = width
    const cropperOpt = {
      id: 'cropper',
      targetId: 'targetCropper',
      pixelRatio: windowInfo.pixelRatio,
      width: width,
      height: height,
      scale: 2.5,
      zoom: 8,
      cut: {
        x: (width - 200) / 2,
        y: (width - 200) / 2,
        width: 200,
        height: 200
      }
    }
    this.setData({
      src: imageUrl,
      cropperOpt: cropperOpt,
    })
    
    // 初始化裁剪器
    this.cropper = new WeCropper(cropperOpt)
    .on('ready', (ctx) => {
        console.log(`wecropper is ready for work!`)
    })
    .on('beforeImageLoad', (ctx) => {
        wx.showToast({
            title: '上传中',
            icon: 'loading',
            duration: 20000
        })
    })
    .on('imageLoad', (ctx) => {
        wx.hideToast()
    })
    // 传入图片
    this.cropper.pushOrign(imageUrl);
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {
    
  },

  // 选择图片
  chooseImage() {
    wx.chooseMedia({
      count: 1, // 仅选1张
      sizeType: ['original', 'compressed'], // 原图/压缩图
      sourceType: ['album', 'camera'], // 相册/相机
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        // 将选择的图片传入裁剪器
        this.cropper.pushOrign(tempFilePath)
        this.setData({src: tempFilePath})
      }
    })
  },
  // 点击裁剪区域（辅助手势操作）
  touchStart(e) {
    this.cropper && this.cropper.touchStart(e);
  },
  touchMove(e) {
    this.cropper && this.cropper.touchMove(e);
  },
  touchEnd(e) {
    this.cropper && this.cropper.touchEnd(e);
  },

  // 获取裁剪后的图片
  getCropperImage() {
    this.cropper.getCropperImage((tempFilePath) => {
      if (!tempFilePath) {
        return wx.showToast({title: '裁剪失败', icon: 'none'})
      }
      // 裁剪成功，tempFilePath 是裁剪后的临时地址
      wx.showToast({title: '裁剪成功', icon: 'success'})

      // 预览图片
      /* wx.previewImage({
        current: tempFilePath,
        urls: [tempFilePath]
      }) */

      //将图片传回首页
      const pages = getCurrentPages() // 获取当前所有已打开的页面栈
      const indexPage = pages.find(page => page.route === 'pages/index/index')
      if (indexPage) {
        // 直接调用index页面的setData，修改它的imageUrl
        indexPage.setData({
          imageUrl: tempFilePath // 裁剪后的图片地址
        })
        // wx.showToast({ title: '图片已更新到首页', icon: 'success' })
      }
      /* wx.navigateBack({
        delta: 1 // 返回上一级页面
      }) */

      // 上传到服务器
      wx.uploadFile({
        url: 'http://127.0.0.1:8000/detect/', // 的后端接口
        method:'POST',
        filePath: tempFilePath,
        name: 'file', // 后端接收文件的字段名
        success: (res) => {
          const data = res.data
          wx.showToast({title: '上传成功', icon: 'success'})
          wx.navigateTo({
            url: "/pages/result/result?data=" + encodeURIComponent(data) 
            +"&src=" + encodeURIComponent(tempFilePath)
          });
        },
        fail: (err) => {
          wx.showToast({title: '上传失败，请重试', icon: 'none'})
          console.error('上传失败：', err)
          const data = null
          wx.navigateTo({
            url: "/pages/result/result?data=" + encodeURIComponent(data) 
            +"&src=" + encodeURIComponent(tempFilePath)
          });
        }
      })
    })
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})