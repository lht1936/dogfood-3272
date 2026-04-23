<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
  },
  onShow: function() {
    console.log('App Show')
  },
  onHide: function() {
    console.log('App Hide')
  }
}
</script>

<style>
/* 每个页面公共css */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.container {
  padding: 20rpx;
}

.btn-primary {
  background-color: #007AFF;
  color: #ffffff;
  border-radius: 8rpx;
  padding: 20rpx 40rpx;
  text-align: center;
  font-size: 32rpx;
}

.btn-primary:active {
  background-color: #0056CC;
}

.btn-secondary {
  background-color: #ffffff;
  color: #007AFF;
  border: 2rpx solid #007AFF;
  border-radius: 8rpx;
  padding: 20rpx 40rpx;
  text-align: center;
  font-size: 32rpx;
}

.btn-danger {
  background-color: #FF3B30;
  color: #ffffff;
  border-radius: 8rpx;
  padding: 20rpx 40rpx;
  text-align: center;
  font-size: 32rpx;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40rpx;
}

.empty-tip {
  text-align: center;
  padding: 80rpx 40rpx;
  color: #999999;
  font-size: 28rpx;
}
</style>
