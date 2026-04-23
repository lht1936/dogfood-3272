<template>
  <view class="container">
    <view class="video-section">
      <video 
        id="videoPlayer"
        class="video-player"
        :src="videoUrl"
        :autoplay="false"
        :controls="true"
        :show-center-play-btn="true"
        :enable-progress-gesture="true"
        @play="onPlay"
        @pause="onPause"
        @timeupdate="onTimeUpdate"
        @ended="onEnded"
        @loadedmetadata="onLoadedMetadata"
      ></video>
    </view>
    
    <view class="control-section">
      <view class="info-card">
        <text class="video-title">{{ videoInfo.filename || '加载中...' }}</text>
        <view class="video-details">
          <text class="detail-item">当前速度: {{ currentSpeed.toFixed(1) }}x</text>
          <text class="detail-item">时长: {{ formatDuration(duration) }}</text>
          <text class="detail-item">当前: {{ formatDuration(currentTime) }}</text>
        </view>
      </view>
      
      <view class="speed-section">
        <view class="section-header">
          <text class="section-title">播放速度</text>
        </view>
        
        <view class="speed-presets">
          <view 
            v-for="speed in speedPresets" 
            :key="speed"
            class="speed-preset"
            :class="{ active: currentSpeed === speed }"
            @click="setSpeed(speed)"
          >
            <text>{{ speed }}x</text>
          </view>
        </view>
        
        <view class="speed-slider-section">
          <view class="slider-header">
            <text class="slider-label">精细调节</text>
            <text class="slider-value">{{ currentSpeed.toFixed(1) }}x</text>
          </view>
          <view class="slider-container">
            <view class="slider-track">
              <view class="slider-fill" :style="{ left: '0%', right: sliderRightPercent }"></view>
              <view class="slider-thumb" :style="{ left: sliderLeftPercent }"></view>
            </view>
            <view class="slider-marks">
              <text class="mark">0.1</text>
              <text class="mark">1.0</text>
              <text class="mark">2.5</text>
              <text class="mark">5.0</text>
            </view>
          </view>
          <input 
            type="range" 
            class="range-input"
            :min="0.1"
            :max="5.0"
            :step="0.1"
            :value="currentSpeed"
            @input="onSliderInput"
          />
        </view>
        
        <view class="custom-speed-section">
          <text class="custom-label">自定义速度 (0.1-5):</text>
          <input 
            type="number" 
            class="custom-input"
            v-model="customSpeedInput"
            placeholder="输入速度"
            step="0.1"
            @confirm="applyCustomSpeed"
          />
          <button class="apply-btn" @click="applyCustomSpeed">应用</button>
        </view>
      </view>
      
      <view class="action-section">
        <view class="action-buttons">
          <button class="action-btn download-btn" @click="downloadCurrentSpeed">
            <text class="btn-icon">↓</text>
            <text class="btn-text">下载当前速度</text>
          </button>
          <button class="action-btn play-btn" @click="togglePlay">
            <text class="btn-icon">{{ isPlaying ? '⏸' : '▶' }}</text>
            <text class="btn-text">{{ isPlaying ? '暂停' : '播放' }}</text>
          </button>
        </view>
        
        <view class="download-options">
          <text class="download-hint">或选择其他速度下载:</text>
          <view class="download-speeds">
            <view 
              v-for="speed in downloadSpeedOptions" 
              :key="speed"
              class="download-speed"
              @click="downloadWithSpeed(speed)"
            >
              <text>{{ speed }}x</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      videoId: '',
      initialSpeed: 1.0,
      currentSpeed: 1.0,
      videoUrl: '',
      videoInfo: {},
      isPlaying: false,
      duration: 0,
      currentTime: 0,
      customSpeedInput: '',
      speedPresets: [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0],
      downloadSpeedOptions: [0.5, 1.0, 1.5, 2.0, 3.0]
    }
  },
  computed: {
    sliderLeftPercent() {
      const percent = ((this.currentSpeed - 0.1) / (5.0 - 0.1)) * 100
      return `${percent}%`
    },
    sliderRightPercent() {
      const percent = ((5.0 - this.currentSpeed) / (5.0 - 0.1)) * 100
      return `${percent}%`
    }
  },
  onLoad(options) {
    this.videoId = options.id || ''
    this.initialSpeed = parseFloat(options.speed) || 1.0
    this.currentSpeed = this.initialSpeed
    this.customSpeedInput = this.currentSpeed.toString()
    this.loadVideoInfo()
  },
  methods: {
    loadVideoInfo() {
      uni.request({
        url: '/api/videos',
        method: 'GET',
        success: (res) => {
          if (res.data.success) {
            const videos = res.data.videos
            const video = videos.find(v => v.id === this.videoId)
            if (video) {
              this.videoInfo = video
              this.videoUrl = `/api/video/${this.videoId}?speed=${this.currentSpeed}`
              this.updateVideoSpeed()
            }
          }
        },
        fail: () => {
          uni.showToast({ title: '加载视频信息失败', icon: 'none' })
        }
      })
    },
    setSpeed(speed) {
      this.currentSpeed = speed
      this.customSpeedInput = speed.toString()
      this.updateVideoSpeed()
    },
    onSliderInput(e) {
      const speed = parseFloat(e.detail.value)
      if (!isNaN(speed) && speed >= 0.1 && speed <= 5.0) {
        this.currentSpeed = speed
        this.customSpeedInput = speed.toString()
        this.updateVideoSpeed()
      }
    },
    applyCustomSpeed() {
      const speed = parseFloat(this.customSpeedInput)
      if (!isNaN(speed) && speed >= 0.1 && speed <= 5.0) {
        this.currentSpeed = speed
        this.updateVideoSpeed()
        uni.showToast({ title: `速度已设置为 ${speed.toFixed(1)}x`, icon: 'success' })
      } else {
        uni.showToast({ title: '请输入0.1-5之间的数值', icon: 'none' })
      }
    },
    updateVideoSpeed() {
      const videoElement = document.getElementById('videoPlayer')
      if (videoElement) {
        const videoTag = videoElement.querySelector('video')
        if (videoTag) {
          videoTag.playbackRate = this.currentSpeed
        }
      }
    },
    onPlay() {
      this.isPlaying = true
    },
    onPause() {
      this.isPlaying = false
    },
    onTimeUpdate(e) {
      this.currentTime = e.detail.currentTime
    },
    onEnded() {
      this.isPlaying = false
    },
    onLoadedMetadata(e) {
      this.duration = e.detail.duration
      this.updateVideoSpeed()
    },
    togglePlay() {
      const videoElement = document.getElementById('videoPlayer')
      if (videoElement) {
        const videoTag = videoElement.querySelector('video')
        if (videoTag) {
          if (this.isPlaying) {
            videoTag.pause()
          } else {
            videoTag.play()
          }
        }
      }
    },
    downloadCurrentSpeed() {
      this.downloadWithSpeed(this.currentSpeed)
    },
    downloadWithSpeed(speed) {
      const downloadUrl = `/api/download/${this.videoId}?speed=${speed}`
      
      const link = document.createElement('a')
      link.href = downloadUrl
      
      let baseName = this.videoInfo.filename || 'video'
      if (baseName.includes('.')) {
        baseName = baseName.substring(0, baseName.lastIndexOf('.'))
      }
      link.download = `${baseName}_${speed.toFixed(1)}x`
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      uni.showToast({ title: `开始下载 ${speed.toFixed(1)}x 版本`, icon: 'success' })
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
.video-section {
  position: relative;
  width: 100%;
  background-color: #000000;
}

.video-player {
  width: 100%;
  height: 450rpx;
  background-color: #000000;
}

.control-section {
  padding: 30rpx;
}

.info-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.video-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
  display: block;
  margin-bottom: 20rpx;
  word-break: break-all;
}

.video-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.detail-item {
  font-size: 26rpx;
  color: #666666;
  padding: 8rpx 16rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
}

.speed-section {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.section-header {
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333333;
}

.speed-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 30rpx;
}

.speed-preset {
  padding: 16rpx 28rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
  border: 2rpx solid transparent;
}

.speed-preset.active {
  background-color: #E8F4FF;
  border-color: #007AFF;
}

.speed-preset.active text {
  color: #007AFF;
  font-weight: bold;
}

.speed-preset text {
  font-size: 26rpx;
  color: #333333;
}

.speed-slider-section {
  margin-bottom: 30rpx;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.slider-label {
  font-size: 28rpx;
  color: #666666;
}

.slider-value {
  font-size: 28rpx;
  color: #007AFF;
  font-weight: bold;
}

.slider-container {
  position: relative;
  margin-bottom: 8rpx;
}

.slider-track {
  position: relative;
  height: 8rpx;
  background-color: #E8E8E8;
  border-radius: 4rpx;
  margin: 30rpx 0;
}

.slider-fill {
  position: absolute;
  top: 0;
  height: 100%;
  background-color: #007AFF;
  border-radius: 4rpx;
}

.slider-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 36rpx;
  height: 36rpx;
  background-color: #ffffff;
  border: 4rpx solid #007AFF;
  border-radius: 50%;
  box-shadow: 0 2rpx 8rpx rgba(0, 122, 255, 0.3);
}

.slider-marks {
  display: flex;
  justify-content: space-between;
}

.mark {
  font-size: 22rpx;
  color: #999999;
}

.range-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  pointer-events: auto;
}

.speed-slider-section {
  position: relative;
}

.custom-speed-section {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex-wrap: wrap;
}

.custom-label {
  font-size: 26rpx;
  color: #666666;
}

.custom-input {
  width: 160rpx;
  height: 72rpx;
  border: 2rpx solid #dddddd;
  border-radius: 8rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  text-align: center;
}

.apply-btn {
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

.apply-btn::after {
  border: none;
}

.action-section {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.action-buttons {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30rpx 20rpx;
  border: none;
  border-radius: 16rpx;
  margin: 0;
}

.action-btn::after {
  border: none;
}

.download-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.play-btn {
  background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
}

.btn-icon {
  font-size: 48rpx;
  color: #ffffff;
  margin-bottom: 8rpx;
}

.btn-text {
  font-size: 26rpx;
  color: #ffffff;
}

.download-options {
  padding-top: 20rpx;
  border-top: 1rpx solid #eeeeee;
}

.download-hint {
  display: block;
  font-size: 26rpx;
  color: #999999;
  margin-bottom: 16rpx;
}

.download-speeds {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.download-speed {
  padding: 12rpx 24rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
  border: 2rpx solid #dddddd;
}

.download-speed text {
  font-size: 26rpx;
  color: #666666;
}
</style>
