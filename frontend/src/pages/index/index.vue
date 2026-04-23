<template>
  <view class="container">
    <view class="upload-section">
      <view class="upload-area" @click="chooseVideo" :class="{ 'drag-over': dragOver }" @dragenter.prevent="dragOver = true" @dragleave.prevent="dragOver = false" @dragover.prevent @drop.prevent="handleDrop">
        <view v-if="!selectedVideo" class="upload-placeholder">
          <text class="upload-icon">+</text>
          <text class="upload-text">点击或拖拽选择视频</text>
          <text class="upload-tip">支持 mp4、avi、mov、mkv、webm 格式</text>
        </view>
        <view v-else class="video-preview">
          <video :src="localVideoUrl" class="preview-video" controls :duration="duration" :show-center-play-btn="true"></video>
          <view class="video-info">
            <text class="video-name">{{ videoName }}</text>
            <text class="video-meta">{{ formatFileSize(fileSize) }} | {{ formatDuration(duration) }}</text>
          </view>
        </view>
      </view>
      
      <view v-if="selectedVideo" class="action-buttons">
        <button class="btn-secondary" @click="resetUpload">重新选择</button>
        <button class="btn-primary" @click="uploadVideo" :disabled="uploading">
          {{ uploading ? '上传中...' : '上传视频' }}
        </button>
      </view>
      
      <view v-if="uploading" class="progress-section">
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: uploadProgress + '%' }"></view>
        </view>
        <text class="progress-text">{{ uploadProgress }}%</text>
      </view>
      
      <view v-if="uploadSuccess" class="success-section">
        <text class="success-icon">✓</text>
        <text class="success-text">视频上传成功！</text>
        <button class="btn-primary" @click="goToHistory">查看历史记录</button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      selectedVideo: null,
      localVideoUrl: '',
      videoName: '',
      fileSize: 0,
      duration: 0,
      uploading: false,
      uploadProgress: 0,
      uploadSuccess: false,
      dragOver: false
    }
  },
  onShow() {
    this.resetUpload()
  },
  methods: {
    chooseVideo() {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'video/*'
      input.onchange = (e) => {
        const file = e.target.files[0]
        if (file) {
          this.handleVideoFile(file)
        }
      }
      input.click()
    },
    handleDrop(e) {
      this.dragOver = false
      const files = e.dataTransfer.files
      if (files.length > 0 && files[0].type.startsWith('video/')) {
        this.handleVideoFile(files[0])
      }
    },
    handleVideoFile(file) {
      const allowedTypes = ['video/mp4', 'video/x-m4v', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
      const ext = file.name.split('.').pop().toLowerCase()
      const allowedExts = ['mp4', 'avi', 'mov', 'mkv', 'webm']
      
      if (!allowedTypes.includes(file.type) && !allowedExts.includes(ext)) {
        uni.showToast({ title: '不支持的视频格式', icon: 'none' })
        return
      }
      
      this.selectedVideo = file
      this.videoName = file.name
      this.fileSize = file.size
      this.localVideoUrl = URL.createObjectURL(file)
      this.uploadSuccess = false
      
      const video = document.createElement('video')
      video.preload = 'metadata'
      video.onloadedmetadata = () => {
        this.duration = video.duration
      }
      video.src = this.localVideoUrl
    },
    resetUpload() {
      this.selectedVideo = null
      this.localVideoUrl = ''
      this.videoName = ''
      this.fileSize = 0
      this.duration = 0
      this.uploading = false
      this.uploadProgress = 0
      this.uploadSuccess = false
    },
    uploadVideo() {
      if (!this.selectedVideo) return
      
      this.uploading = true
      this.uploadProgress = 0
      
      const formData = new FormData()
      formData.append('video', this.selectedVideo)
      
      const xhr = new XMLHttpRequest()
      
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          this.uploadProgress = Math.round((e.loaded / e.total) * 100)
        }
      }
      
      xhr.onload = () => {
        this.uploading = false
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText)
          if (response.success) {
            this.uploadSuccess = true
            uni.showToast({ title: '上传成功', icon: 'success' })
          } else {
            uni.showToast({ title: response.error || '上传失败', icon: 'none' })
          }
        } else {
          uni.showToast({ title: '上传失败，请重试', icon: 'none' })
        }
      }
      
      xhr.onerror = () => {
        this.uploading = false
        uni.showToast({ title: '网络错误，请重试', icon: 'none' })
      }
      
      xhr.open('POST', '/api/upload', true)
      xhr.send(formData)
    },
    goToHistory() {
      uni.switchTab({ url: '/pages/history/history' })
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    formatDuration(seconds) {
      if (!seconds || isNaN(seconds)) return '0:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.upload-section {
  padding: 40rpx;
}

.upload-area {
  width: 100%;
  min-height: 400rpx;
  border: 4rpx dashed #cccccc;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
  transition: all 0.3s;
}

.upload-area.drag-over {
  border-color: #007AFF;
  background-color: #E8F4FF;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx;
}

.upload-icon {
  font-size: 120rpx;
  color: #cccccc;
  margin-bottom: 20rpx;
}

.upload-text {
  font-size: 32rpx;
  color: #666666;
  margin-bottom: 16rpx;
}

.upload-tip {
  font-size: 24rpx;
  color: #999999;
}

.video-preview {
  width: 100%;
  padding: 20rpx;
}

.preview-video {
  width: 100%;
  height: 360rpx;
  background-color: #000000;
  border-radius: 8rpx;
}

.video-info {
  padding: 20rpx 0;
}

.video-name {
  font-size: 28rpx;
  color: #333333;
  display: block;
  margin-bottom: 8rpx;
  word-break: break-all;
}

.video-meta {
  font-size: 24rpx;
  color: #999999;
}

.action-buttons {
  display: flex;
  gap: 20rpx;
  margin-top: 40rpx;
}

.action-buttons button {
  flex: 1;
  border: none;
  margin: 0;
}

.action-buttons button[disabled] {
  opacity: 0.6;
}

.progress-section {
  margin-top: 40rpx;
  padding: 20rpx;
  background-color: #ffffff;
  border-radius: 8rpx;
}

.progress-bar {
  width: 100%;
  height: 12rpx;
  background-color: #E8E8E8;
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #007AFF;
  transition: width 0.3s;
}

.progress-text {
  display: block;
  text-align: center;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #666666;
}

.success-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 40rpx;
  margin-top: 40rpx;
  background-color: #F0FFF0;
  border-radius: 16rpx;
}

.success-icon {
  font-size: 80rpx;
  color: #4CD964;
  margin-bottom: 20rpx;
}

.success-text {
  font-size: 32rpx;
  color: #333333;
  margin-bottom: 40rpx;
}
</style>
