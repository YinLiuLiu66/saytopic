<script setup>
import { ref, computed, onUnmounted } from 'vue'
import QRCode from 'qrcode'
import AudioRecorder from '../components/AudioRecorder.vue'
import CameraCapture from '../components/CameraCapture.vue'
import QrCodeCard from '../components/QrCodeCard.vue'

const audioUrl = ref('')
const filename = ref('')
const imageUrl = ref('')
const imageUploaded = ref(false)
const showUploadQr = ref(false)
const uploadQrDataUrl = ref('')
let pollingTimer = null

const showImageSection = computed(() => audioUrl.value && !imageUploaded.value)
const imageUploadPath = computed(() => {
  if (!filename.value) return ''
  const base = filename.value.replace(/\.[^.]+$/, '')
  return `${window.location.origin}/upload-image/${base}`
})

function onAudioUploaded({ url, filename: name }) {
  audioUrl.value = url
  filename.value = name
  showUploadQr.value = true
  generateUploadQr()
  startPolling()
}

async function generateUploadQr() {
  if (imageUploadPath.value) {
    uploadQrDataUrl.value = await QRCode.toDataURL(imageUploadPath.value, {
      width: 200,
      margin: 2,
      color: { dark: '#2D3748', light: '#ffffff' },
    })
  }
}

const IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

function startPolling() {
  stopPolling()
  pollingTimer = setInterval(async () => {
    try {
      const base = filename.value.replace(/\.[^.]+$/, '')
      for (const ext of IMAGE_EXTENSIONS) {
        const url = `/api/image/${base}${ext}`
        try {
          const res = await fetch(url, { method: 'HEAD' })
          if (res.ok) {
            imageUrl.value = url
            imageUploaded.value = true
            showUploadQr.value = false
            stopPolling()
            return
          }
        } catch (e) {
          // 继续尝试下一个扩展名
        }
      }
    } catch (e) {
      // 继续轮询
    }
  }, 3000)
}

function stopPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

function skipImage() {
  stopPolling()
  imageUploaded.value = true
  showUploadQr.value = false
}

function onImageCaptured({ url, filename }) {
  stopPolling()
  imageUrl.value = url
  imageUploaded.value = true
  showUploadQr.value = false
}

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="home">
    <!-- 装饰背景元素 -->
    <div class="bg-decor">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <!-- 主内容区 -->
    <main class="home-main">
      <!-- Hero 标题区 -->
      <header class="hero">
        <div class="hero-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
          <span>声音家书</span>
        </div>
        <h1 class="hero-title">立德思源，感恩笃行</h1>
        <p class="hero-desc">
          录下你的感恩之声，生成专属二维码明信片，让声音穿越时空温暖人心
        </p>
      </header>

      <!-- 录音区域 -->
      <section class="section recorder-section">
        <AudioRecorder @uploaded="onAudioUploaded" />
      </section>

      <!-- 图片上传二维码区域（可选） -->
      <Transition name="slide-up">
        <section v-if="showImageSection" class="section image-section">
          <div class="section-header">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <div>
              <h3 class="section-title">添加一张照片</h3>
              <p class="section-desc">为这段声音配上专属图片（可选）</p>
            </div>
          </div>
          <div class="upload-options">
            <div class="upload-option">
              <h4 class="option-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
                电脑拍照
              </h4>
              <CameraCapture
                :audio-filename="filename"
                @captured="onImageCaptured"
              />
            </div>
            <div class="upload-option-divider">
              <span class="divider-text">或</span>
            </div>
            <div class="upload-option">
              <h4 class="option-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <rect x="7" y="7" width="3" height="3"/>
                  <rect x="14" y="7" width="3" height="3"/>
                  <rect x="7" y="14" width="10" height="3"/>
                </svg>
                扫码上传
              </h4>
              <div class="qr-upload">
                <div class="qr-frame">
                  <img v-if="uploadQrDataUrl" :src="uploadQrDataUrl" alt="图片上传二维码" />
                </div>
                <p class="qr-hint">用手机扫描二维码上传照片</p>
              </div>
            </div>
          </div>
          <button class="skip-btn" @click="skipImage">
            跳过，直接生成明信片
          </button>
        </section>
      </Transition>

      <!-- 明信片区域 -->
      <Transition name="slide-up">
        <section v-if="audioUrl && imageUploaded" class="section card-section">
          <div class="section-header center">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M22 4L12 13l-10-9"/>
              </svg>
            </div>
            <div>
              <h3 class="section-title">你的声音明信片</h3>
              <p class="section-desc">扫码即可播放这段感恩之声</p>
            </div>
          </div>
          <QrCodeCard
            :audio-url="audioUrl"
            :filename="filename"
            :image-url="imageUrl"
          />
        </section>
      </Transition>

      <!-- 页脚 -->
      <footer class="home-footer">
        <p>SayTopic - 声音家书，传递感恩</p>
      </footer>
    </main>
  </div>
</template>

<style scoped>
.home {
  position: relative;
  min-height: 100vh;
  padding: 0 16px;
}

/* ===== 装饰背景 ===== */
.bg-decor {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
}

.bg-circle-1 {
  width: 500px;
  height: 500px;
  background: var(--primary-400);
  top: -150px;
  right: -100px;
  animation: float-slow 20s ease-in-out infinite;
}

.bg-circle-2 {
  width: 300px;
  height: 300px;
  background: var(--accent-coral);
  bottom: 10%;
  left: -80px;
  animation: float-slow 15s ease-in-out infinite reverse;
}

.bg-circle-3 {
  width: 200px;
  height: 200px;
  background: var(--primary-300);
  top: 40%;
  right: 5%;
  animation: float-slow 25s ease-in-out infinite;
}

@keyframes float-slow {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(20px, -15px); }
  50% { transform: translate(-10px, 20px); }
  75% { transform: translate(15px, 10px); }
}

/* ===== 主内容 ===== */
.home-main {
  position: relative;
  z-index: 1;
  max-width: 640px;
  margin: 0 auto;
  padding: 40px 0 60px;
}

/* ===== Hero ===== */
.hero {
  text-align: center;
  margin-bottom: 48px;
  animation: hero-enter 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes hero-enter {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: var(--primary-100);
  border: 1px solid var(--primary-200);
  border-radius: var(--radius-full);
  color: var(--primary-600);
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 40px;
  font-weight: 700;
  color: var(--neutral-800);
  margin: 0;
  line-height: 1.3;
  letter-spacing: 6px;
}

.hero-desc {
  font-size: 15px;
  color: var(--neutral-500);
  margin: 16px 0 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.7;
}

/* ===== 分段 ===== */
.section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.section-header.center {
  justify-content: center;
  text-align: center;
}

.section-header.center .section-header {
  flex-direction: column;
}

.section-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-100);
  border-radius: var(--radius-md);
  color: var(--primary-500);
  flex-shrink: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0 0 2px;
}

.section-desc {
  font-size: 13px;
  color: var(--neutral-400);
  margin: 0;
}

/* ===== 图片上传区域 ===== */
.image-section {
  animation: section-appear 0.5s ease-out;
}

.upload-options {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.upload-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  background: white;
  border: 2px dashed var(--primary-200);
  border-radius: var(--radius-md);
}

.option-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--neutral-600);
  margin: 0 0 16px;
}

.upload-option-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 40px;
  padding-top: 80px;
}

.divider-text {
  font-size: 13px;
  color: var(--neutral-400);
}

.qr-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.qr-frame {
  width: 160px;
  height: 160px;
  padding: 8px;
  background: white;
  border: 2px solid var(--primary-200);
  border-radius: var(--radius-sm);
}

.qr-frame img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.qr-hint {
  font-size: 13px;
  color: var(--neutral-500);
  margin: 0;
  text-align: center;
}

.skip-btn {
  display: block;
  margin: 16px auto 0;
  padding: 8px 20px;
  background: transparent;
  border: 1.5px dashed var(--neutral-300);
  border-radius: var(--radius-full);
  color: var(--neutral-400);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.skip-btn:hover {
  border-color: var(--primary-400);
  color: var(--primary-500);
  background: var(--primary-100);
}

/* ===== 明信片区域 ===== */
.card-section {
  margin-top: 48px;
}

/* ===== 过渡动画 ===== */
.slide-up-enter-active {
  animation: slide-up 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.slide-up-leave-active {
  animation: slide-up 0.3s ease-in reverse;
}

@keyframes slide-up {
  0% {
    opacity: 0;
    transform: translateY(24px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes section-appear {
  0% {
    opacity: 0;
    transform: translateY(16px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== 页脚 ===== */
.home-footer {
  text-align: center;
  padding: 40px 0 0;
  font-size: 12px;
  color: var(--neutral-400);
  font-family: var(--font-mono);
  letter-spacing: 1px;
}

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .home-main {
    padding: 24px 0 40px;
  }

  .hero-title {
    font-size: 28px;
    letter-spacing: 4px;
  }

  .hero-desc {
    font-size: 14px;
  }

  .section-header {
    gap: 10px;
  }

  .upload-options {
    flex-direction: column;
    gap: 12px;
  }

  .upload-option-divider {
    width: auto;
    padding-top: 0;
  }
}
</style>
