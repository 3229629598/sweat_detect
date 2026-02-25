// index.js
import md5 from '../../miniprogram_npm/blueimp-md5/index.js'

Page({
  data: {
    imageUrl: '/images/picture/home_img.jpg', // 选中的图片临时路径
    imageMd5: 0,
  },
  onDisplay() {
    this.setData({ show: true });
  },
  onClose() {
    this.setData({ show: false });
  },
  formatDate(date) {
    date = new Date(date);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  },
  onConfirm(event) {
    this.setData({
      show: false,
      date: this.formatDate(event.detail),
    });
  },
  /**
   * 计算MD5哈希值
   * @param {string} filePath 文件路径
   */
  calculateFileHash(filePath){
    const fs = wx.getFileSystemManager(); 
    fs.readFile({
      filePath: filePath,
      encoding: 'binary', // 以二进制读取
      success: (fileRes) => {
        const imageMd5 = md5(fileRes.data);
        console.log('小程序端计算的MD5:', imageMd5);
        this.setData({
          imageMd5: imageMd5,
        })
      },
      fail: (err) => {
        console.error('读取图片失败:', err);
        wx.showToast({title: '读取图片失败', icon: 'none'});
      }
    });
  },

  handleDetect(){
    if (!this.data.imageUrl) {
      wx.showToast({ title: '请先选择图片', icon: 'none' });
      return;
    }
    this.calculateFileHash(this.data.imageUrl);
    // 上传到服务器
    wx.uploadFile({
      url: 'http://192.168.1.6:8000/detect/', // 的后端接口
      method:'POST',
      filePath: this.data.imageUrl,
      name: 'file', // 后端接收文件的字段名
      success: (res) => {
        const data = res.data;
        wx.showToast({title: '上传成功', icon: 'success'});
        wx.navigateTo({
          url: "/pages/result/result?data=" + encodeURIComponent(data) 
          +"&src=" + encodeURIComponent(this.data.imageUrl)
        });
      },
      fail: (err) => {
        wx.showToast({title: '上传失败，请重试', icon: 'none'});
        console.error('上传失败：', err);
        const data = null;
        wx.navigateTo({
          url: "/pages/result/result?data=" + encodeURIComponent(data) 
          +"&src=" + encodeURIComponent(this.data.imageUrl)
        });
      }
    })
  },

  /**
   * 通用选择媒体方法
   * @param {string} sourceType 来源：camera(相机) / album(相册)
   */
  chooseMedia() {
    wx.chooseMedia({
      count: 1, // 最多选择1张
      mediaType: ['image'], // 只选图片
      sourceType: ['camera','album'], // 来源类型
      camera: 'back', // 使用后置摄像头
      success: (res) => {
        // 成功获取图片，更新预览路径
        const tempFilePath = res.tempFiles[0].tempFilePath
        this.setData({
          imageUrl: tempFilePath
        })
        console.log('选中的图片路径：', tempFilePath)
        wx.editImage({
          src: tempFilePath, // 拍摄后的图片路径
          success: (editRes) => {
            // 编辑后的图片路径
            const editedPath = editRes.tempFilePath;
            console.log('选中的图片路径：', editedPath);
            this.setData({
              imageUrl: editedPath
            })
          },
          fail(editErr) {
            console.error('编辑图片失败：', editErr);
            wx.showToast({title: '编辑失败', icon: 'none'});            
          }
        });
      },
      fail: (err) => {
        if (err.errMsg !== 'chooseMedia:fail cancel') {
          wx.showToast({
            title: '选择图片失败',
            icon: 'none'
          })
          console.error('选择图片失败：', err)
        }
      }
    })
  },
})
