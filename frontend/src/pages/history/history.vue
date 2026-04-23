<template>
  <view class="container">
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>
    
    <view v-else-if="videos.length === 0" class="empty-tip">
      <text>暂无历史视频</text>
      <text class="empty-sub-tip">上传您的第一个视频吧</text>
    </view>
    
    <view v-else class="video-list">
      <view 
        v-for="video in videos" 
        :key="video.id" 
        class="video-item"
        @click="playVideo(video)"
      >
        <view class="video-cover">
          <view class="cover-placeholder">
            <text class="play-icon">▶</text>
          </view>
          <view class="video-duration">{{ formatDuration(video.duration) }}</view>
        </view>
        <view class="video-info">
          <text class="video-name">{{ video.filename }}</text>
          <view class="video-meta">
            <text class="meta-item">{{ formatFileSize(video.file_size) }}</text>
            <text class="meta-item">•</text>
            <text class="meta-item">{{ formatDate(video.upload_time) }}</text>
          </view>
        </view>
        <view class="video-actions">
          <button class="action-btn" @click.stop="downloadVideo(video)">
            <text class="action-icon">↓</text>
            <text class="action-text">下载</text>
          </button>
          <button class="action-btn delete-btn" @click.stop="deleteVideo(video)">
            <text class="action-icon">×</text>
            <text class="action-text">删除</text>
          </button>
        </view>
      </view>
    </view>
    
    <view v-if="showSpeedModal" class="modal-mask" @click="closeSpeedModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">选择播放速度</text>
          <text class="modal-close" @click="closeSpeedModal">×</text>
        </view>
        <view class="speed-options">
          <view 
            v-for="speed in speedOptions" 
            :key="speed"
            class="speed-option"
            :class="{ active: selectedSpeed === speed }"
            @click="selectSpeed(speed)"
          >
            <text>{{ speed }}x</text>
          </view>
        </view>
        <view class="custom-speed">
          <text class="custom-label">自定义速度 (0.1-5x):</text>
          <input 
            type="number" 
            class="custom-input" 
            v-model="customSpeed"
            placeholder="输入速度"
            step="0.1"
            min="0.1"
            max="5"
          />
          <button class="custom-btn" @click="applyCustomSpeed">应用</button>
        </view>
        <view class="modal-footer">
          <button class="modal-btn confirm" @click="confirmPlay">确定播放</button>
        </view>
      </view>
    </view>
    
    <view v-if="showDownloadModal" class="modal-mask" @click="closeDownloadModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">选择下载速度</text>
          <text class="modal-close" @click="closeDownloadModal">×</text>
        </view>
        <view class="speed-options">
          <view 
            v-for="speed in speedOptions" 
            :key="speed"
            class="speed-option"
            :class="{ active: downloadSpeed === speed }"
            @click="selectDownloadSpeed(speed)"
          >
            <text>{{ speed }}x</text>
          </view>
        </view>
        <view class="modal-footer">
          <button class="modal-btn confirm" @click="confirmDownload">确定下载</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      videos: [],
      loading: true,
      showSpeedModal: false,
      showDownloadModal: false,
      selectedVideo: null,
      selectedSpeed: 1.0,
      downloadSpeed: 1.0,
      customSpeed: '',
      speedOptions: [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
    }
  },
  onShow() {
    this.loadVideos()
  },
  methods: {
    loadVideos() {
      this.loading = true
      uni.request({
        url: '/api/videos',
        method: 'GET',
        success: (res) => {
          if (res.data.success) {
            this.videos = res.data.videos
          }
        },
        fail: () => {
          uni.showToast({ title: '加载失败', icon: 'none' })
        },
        complete: () => {
          this.loading = false
        }
      })
    },
    playVideo(video) {
      this.selectedVideo = video
      this.selectedSpeed = 1.0
      this.customSpeed = ''
      this.showSpeedModal = true
    },
    closeSpeedModal() {
      this.showSpeedModal = false
      this.selectedVideo = null
    },
    selectSpeed(speed) {
      this.selectedSpeed = speed
      this.customSpeed = ''
    },
    applyCustomSpeed() {
      const speed = parseFloat(this.customSpeed)
      if (!isNaN(speed) && speed >= 0.1 && speed <= 5.0) {
        this.selectedSpeed = speed
      } else {
        uni.showToast({ title: '请输入0.1-5之间的数值', icon: 'none' })
      }
    },
    confirmPlay() {
      if (this.selectedVideo) {
        uni.navigateTo({
          url: `/pages/player/player?id=${this.selectedVideo.id}&speed=${this.selectedSpeed}`
        })
        this.closeSpeedModal()
      }
    },
    downloadVideo(video) {
      this.selectedVideo = video
      this.downloadSpeed = 1.0
      this.showDownloadModal = true
    },
    closeDownloadModal() {
      this.showDownloadModal = false
      this.selectedVideo = null
    },
    selectDownloadSpeed(speed) {
      this.downloadSpeed = speed
    },
    confirmDownload() {
      if (this.selectedVideo) {
        const downloadUrl = `/api/download/${this.selectedVideo.id}?speed=${this.downloadSpeed}`
        
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = `${this.selectedVideo.filename}_${this.downloadSpeed}x`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        uni.showToast({ title: '开始下载', icon: 'success' })
        this.closeDownloadModal()
      }
    },
    deleteVideo(video) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个视频吗？',
        success: (res) => {
          if (res.confirm) {
            uni.request({
              url: `/api/video/${video.id}`,
              method: 'DELETE',
              success: (res) => {
                if (res.data.success) {
                  uni.showToast({ title: '删除成功', icon: 'success' })
                  this.loadVideos()
                } else {
                  uni.showToast({ title: res.data.error || '删除失败', icon: 'none' })
                }
              },
              fail: () => {
                uni.showToast({ title: '删除失败', icon: 'none' })
              }
            })
          }
        }
      })
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      const hour = date.getHours().toString().padStart(2, '0')
      const minute = date.getMinutes().toString().padStart(2, '0')
      return `${year}-${month}-${day} ${hour}:${minute}`
    },
    formatFileSize(bytes) {
      if (!bytes || bytes === 0) return '0 B'
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
.video-list {
  padding: 20rpx;
}

.video-item {
  background-color: #ffffff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.video-cover {
  position: relative;
  width: 100%;
  height: 400rpx;
  background-color: #000000;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.play-icon {
  font-size: 80rpx;
  color: #ffffff;
  opacity: 0.8;
}

.video-duration {
  position: absolute;
  right: 16rpx;
  bottom: 16rpx;
  background-color: rgba(0, 0, 0, 0.7);
  color: #ffffff;
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

.video-info {
  padding: 20rpx;
}

.video-name {
  font-size: 30rpx;
  color: #333333;
  display: block;
  margin-bottom: 12rpx;
  word-break: break-all;
}

.video-meta {
  display: flex;
  align-items: center;
}

.meta-item {
  font-size: 24rpx;
  color: #999999;
}

.meta-item:nth-child(2) {
  margin: 0 12rpx;
}

.video-actions {
  display: flex;
  border-top: 1rpx solid #eeeeee;
}

.action-btn {
  flex: 1;
  border: none;
  background: none;
  margin: 0;
  padding: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.action-btn::after {
  border: none;
}

.action-icon {
  font-size: 32rpx;
  color: #007AFF;
}

.action-text {
  font-size: 26rpx;
  color: #007AFF;
}

.delete-btn .action-icon,
.delete-btn .action-text {
  color: #FF3B30;
}

.empty-sub-tip {
  display: block;
  margin-top: 16rpx;
  font-size: 24rpx;
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  width: 90%;
  max-width: 600rpx;
  background-color: #ffffff;
  border-radius: 16rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx;
  border-bottom: 1rpx solid #eeeeee;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
}

.modal-close {
  font-size: 48rpx;
  color: #999999;
  line-height: 1;
}

.speed-options {
  display: flex;
  flex-wrap: wrap;
  padding: 30rpx;
  gap: 20rpx;
}

.speed-option {
  width: calc(33.333% - 14rpx);
  padding: 20rpx;
  text-align: center;
  border: 2rpx solid #dddddd;
  border-radius: 8rpx;
}

.speed-option.active {
  border-color: #007AFF;
  background-color: #E8F4FF;
}

.speed-option.active text {
  color: #007AFF;
  font-weight: bold;
}

.speed-option text {
  font-size: 28rpx;
  color: #333333;
}

.custom-speed {
  display: flex;
  align-items: center;
  padding: 0 30rpx 30rpx;
  gap: 16rpx;
}

.custom-label {
  font-size: 26rpx;
  color: #666666;
  white-space: nowrap;
}

.custom-input {
  flex: 1;
  height: 72rpx;
  border: 2rpx solid #dddddd;
  border-radius: 8rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
}

.custom-btn {
  background-color: #007AFF;
  color: #ffffff;
  border: none;
  border-radius: 8rpx;
  padding: 0 30rpx;
  height: 72rpx;
  line-height: 72rpx;
  font-size: 28rpx;
  margin: 0;
}

.custom-btn::after {
  border: none;
}

.modal-footer {
  padding: 20rpx 30rpx 30rpx;
}

.modal-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  border: none;
  border-radius: 8rpx;
  font-size: 32rpx;
  margin: 0;
}

.modal-btn::after {
  border: none;
}

.modal-btn.confirm {
  background-color: #007AFF;
  color: #ffffff;
}
</style>
