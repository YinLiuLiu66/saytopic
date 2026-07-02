<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import WaveformCanvas from '../components/WaveformCanvas.vue'

const route = useRoute()
const filename = computed(() => route.params.filename)
const audioUrl = computed(() => `/api/audio/${filename.value}`)
const playUrl = computed(() => window.location.href)
const showPage = ref(false)

onMounted(() => {
  setTimeout(() => { showPage.value = true }, 100)
})
</script>

<template>
  <div class="play-view">
    <!-- 装饰背景 -->
    <div class="bg-decor">
      <div class="bg-ring bg-ring-1"></div>
      <div class="bg-ring bg-ring-2"></div>
    </div>

    <Transition name="page-enter">
      <main v-if="showPage" class="play-main">
        <!-- 品牌标识 -->
        <div class="brand-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
          <span>SayTopic</span>
        </div>

        <!-- 播放卡片 -->
        <div class="player-card">
          <!-- 顶部装饰 -->
          <div class="card-header">
            <div class="header-line"></div>
            <h1 class="card-title">声音家书</h1>
            <p class="card-subtitle">Voice Letter</p>
            <div class="header-line"></div>
          </div>

          <!-- 唱片动画 -->
          <div class="vinyl-container">
            <div class="vinyl">
              <div class="vinyl-inner">
                <div class="vinyl-label">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                    <path d="M9 18V5l12-2v13"/>
                    <circle cx="6" cy="18" r="3"/>
                    <circle cx="18" cy="16" r="3"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- 波形展示 -->
          <div class="waveform-section">
            <WaveformCanvas :audio-url="audioUrl" :height="100" :width="460" color-theme="primary" />
          </div>

          <!-- 播放器 -->
          <div class="audio-player">
            <audio controls :src="audioUrl" class="audio-element"></audio>
          </div>

          <!-- 提示文字 -->
          <div class="play-hint">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
            <span>戴上耳机，沉浸聆听这段感恩之声</span>
          </div>

          <!-- 底部 -->
          <div class="card-footer">
            <p class="footer-text">听见心声 · 传递感恩</p>
          </div>
        </div>

        <!-- 页脚 -->
        <footer class="play-footer">
          <p>SayTopic - 声音家书，传递感恩</p>
        </footer>
      </main>
    </Transition>
  </div>
</template>

<style scoped>
.play-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  position: relative;
  overflow: hidden;
}

/* ===== 装饰背景 ===== */
.bg-decor {
  position: fixed;
  inset: 0;
  pointer-events: none;
}

.bg-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid var(--primary-200);
  opacity: 0.3;
}

.bg-ring-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -150px;
  animation: ring-rotate 30s linear infinite;
}

.bg-ring-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -100px;
  animation: ring-rotate 20s linear infinite reverse;
}

@keyframes ring-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ===== 页面过渡 ===== */
.page-enter-enter-active {
  animation: page-in 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes page-in {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.97);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ===== 主内容 ===== */
.play-main {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 520px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ===== 品牌标识 ===== */
.brand-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  background: var(--bg-card);
  border: 1.5px solid var(--primary-200);
  border-radius: var(--radius-full);
  color: var(--primary-600);
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-display);
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
}

/* ===== 播放卡片 ===== */
.player-card {
  width: 100%;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--primary-200);
}

/* 卡片头部 */
.card-header {
  padding: 28px 32px 20px;
  text-align: center;
  background: linear-gradient(135deg, var(--primary-100), var(--primary-200));
  border-bottom: 1px dashed var(--primary-300);
}

.header-line {
  width: 40px;
  height: 2px;
  background: var(--primary-300);
  margin: 0 auto 12px;
  border-radius: 1px;
}

.card-header .header-line:last-child {
  margin: 12px auto 0;
}

.card-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--neutral-700);
  margin: 0;
  letter-spacing: 4px;
}

.card-subtitle {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--neutral-400);
  margin: 6px 0 0;
  letter-spacing: 3px;
  text-transform: uppercase;
}

/* 唱片动画 */
.vinyl-container {
  display: flex;
  justify-content: center;
  padding: 28px 0 16px;
}

.vinyl {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    var(--neutral-700) 0deg,
    var(--neutral-800) 45deg,
    var(--neutral-700) 90deg,
    var(--neutral-800) 135deg,
    var(--neutral-700) 180deg,
    var(--neutral-800) 225deg,
    var(--neutral-700) 270deg,
    var(--neutral-800) 315deg,
    var(--neutral-700) 360deg
  );
  display: flex;
  align-items: center;
  justify-content: center;
  animation: vinyl-spin 4s linear infinite;
  box-shadow:
    0 4px 20px rgba(0, 0, 0, 0.2),
    inset 0 0 0 3px var(--neutral-600);
}

.vinyl-inner {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-400);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 3px var(--primary-300);
}

.vinyl-label {
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes vinyl-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 波形区域 */
.waveform-section {
  padding: 0 24px;
}

/* 播放器 */
.audio-player {
  padding: 20px 24px;
}

.audio-element {
  width: 100%;
  height: 48px;
  border-radius: 24px;
}

/* 播放提示 */
.play-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 24px 16px;
  font-size: 13px;
  color: var(--neutral-400);
}

/* 底部 */
.card-footer {
  padding: 16px 24px;
  text-align: center;
  background: var(--primary-100);
  border-top: 1px dashed var(--primary-300);
}

.footer-text {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--primary-500);
  letter-spacing: 2px;
  margin: 0;
}

/* 页脚 */
.play-footer {
  margin-top: 32px;
  font-size: 12px;
  color: var(--neutral-400);
  font-family: var(--font-mono);
  letter-spacing: 1px;
}

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .card-header {
    padding: 20px 20px 16px;
  }

  .card-title {
    font-size: 24px;
  }

  .waveform-section {
    padding: 0 16px;
  }

  .audio-player {
    padding: 16px;
  }
}
</style>
