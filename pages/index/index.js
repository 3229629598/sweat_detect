// index.js
Page({
  data: {
    imageUrl: '/images/picture/home_img.jpg' // 选中的图片临时路径
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

  handleCamera(){
    // this.chooseMedia('camera')
    wx.chooseMedia({
      count: 1, // 最多选择1张
      mediaType: ['image'], // 只选图片
      sourceType: ['camera'], // 来源类型
      camera: 'back', // 使用后置摄像头
      success: (res) => {
        // 成功获取图片，更新预览路径
        const tempFilePath = res.tempFiles[0].tempFilePath;
        this.setData({
          imageUrl: tempFilePath
        })
        wx.showToast({title: '请编辑图片', icon: 'none', duration: 1000});
        wx.editImage({
          src: tempFilePath, // 拍摄后的图片路径
          editOptions: {
            crop: true,   // 允许裁剪
            rotate: true, // 允许旋转
            filter: true, // 允许加滤镜
            adjust: true, // 允许调整亮度/对比度等
          },
          success: (editRes) => {
            // 编辑后的图片路径
            const editedPath = editRes.tempFilePath;
            console.log('拍摄的图片路径：', editedPath);
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
        // 处理失败情况（比如用户取消授权/选择）
        if (err.errMsg !== 'chooseMedia:fail cancel') {
          wx.showToast({
            title: '拍照失败',
            icon: 'none'
          })
          console.error('拍照失败：', err)
        }
      }
    })
  },
  
  handleAlbum(){
    // this.chooseMedia('album')
    wx.chooseMedia({
      count: 1, // 最多选择1张
      mediaType: ['image'], // 只选图片
      sourceType: ['album'], // 来源类型
      camera: 'back', // 使用后置摄像头
      success: (res) => {
        // 成功获取图片，更新预览路径
        const tempFilePath = res.tempFiles[0].tempFilePath;
        this.setData({
          imageUrl: tempFilePath
        });
        wx.editImage({
          src: tempFilePath, // 拍摄后的图片路径
          editOptions: {
            crop: true,   // 允许裁剪
            rotate: true, // 允许旋转
            filter: true, // 允许加滤镜
            adjust: true, // 允许调整亮度/对比度等
          },
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
        // 处理失败情况（比如用户取消授权/选择）
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

  handleDetect(){
    if (!this.data.imageUrl) {
      wx.showToast({ title: '请先选择图片', icon: 'none' });
      return;
    }
    // 跳转到裁剪页，并传递图片路径
    wx.navigateTo({
      url: "/pages/crop/crop?imageUrl=" + encodeURIComponent(this.data.imageUrl)
    });
  },

  /**
   * 通用选择媒体方法
   * @param {string} sourceType 来源：camera(相机) / album(相册)
   */
  chooseMedia(sourceType) {
    wx.chooseMedia({
      count: 1, // 最多选择1张
      mediaType: ['image'], // 只选图片
      sourceType: [sourceType], // 来源类型
      camera: 'back', // 使用后置摄像头
      success: (res) => {
        // 成功获取图片，更新预览路径
        const tempFilePath = res.tempFiles[0].tempFilePath
        this.setData({
          imageUrl: tempFilePath
        })
        // 这里可以添加后续逻辑：比如上传图片到服务器进行汗液成分检测
        console.log('选中的图片路径：', tempFilePath)
        // this.uploadImage(tempFilePath) // 调用上传方法
      },
      fail: (err) => {
        // 处理失败情况（比如用户取消授权/选择）
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
