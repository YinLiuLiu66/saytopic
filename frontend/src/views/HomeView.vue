<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import QRCode from 'qrcode'
import AudioRecorder from '../components/AudioRecorder.vue'
import CameraCapture from '../components/CameraCapture.vue'
import QrCodeCard from '../components/QrCodeCard.vue'

const audioUrl = ref('')
const filename = ref('')
const imageUrl = ref('')
const uploadQrDataUrl = ref('')
const recorderKey = ref(0)
const step = ref('record') // record | image | card
const stageScale = ref(1)
let pollingTimer = null

// 八字艺术字背景：左右两列竖排，不旋转，右列整体下移错开
const BG_COLUMNS = [
  { side: 'left', chars: ['立', '德', '思', '源'] },
  { side: 'right', chars: ['感', '恩', '笃', '行'] },
]

const stageStyle = computed(() => ({
  transform: `scale(${stageScale.value})`,
}))

// 小于基准分辨率时整体等比缩放，保证单屏内按钮不被裁掉
function updateStageScale() {
  const scale = Math.min(1, window.innerWidth / 1200, window.innerHeight / 700)
  stageScale.value = scale
}

const uploadQrTarget = computed(() => {
  if (!filename.value) return ''
  const base = filename.value.replace(/\.[^.]+$/, '')
  return `${window.location.origin}/upload-image/${base}`
})

function resetCreation() {
  stopPolling()
  audioUrl.value = ''
  filename.value = ''
  imageUrl.value = ''
  uploadQrDataUrl.value = ''
  step.value = 'record'
  recorderKey.value++
}

function onAudioUploaded({ url, filename: name }) {
  if (step.value !== 'record') return
  audioUrl.value = url
  filename.value = name
  step.value = 'image'
  generateUploadQr()
  startPolling()
}

async function generateUploadQr() {
  if (!uploadQrTarget.value) return
  uploadQrDataUrl.value = await QRCode.toDataURL(uploadQrTarget.value, {
    width: 200,
    margin: 2,
    color: { dark: '#2D3748', light: '#ffffff' },
  })
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
            showCard(url)
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

function showCard(url) {
  if (step.value === 'card') return
  stopPolling()
  if (url) imageUrl.value = url
  step.value = 'card'
}

function onImageCaptured({ url }) {
  showCard(url)
}

onMounted(() => {
  updateStageScale()
  window.addEventListener('resize', updateStageScale)
})

onUnmounted(() => {
  stopPolling()
  window.removeEventListener('resize', updateStageScale)
})
</script>

<template>
  <div class="home">
    <!-- 校园线稿：底部对齐，压在艺术字下面 -->
    <img class="bg-building" src="/campus-building.png" alt="" aria-hidden="true" />

    <!-- 八字艺术字背景：左右两列竖排 -->
    <div class="bg-text" aria-hidden="true">
      <div
        v-for="col in BG_COLUMNS"
        :key="col.side"
        class="bg-col"
        :class="`bg-col-${col.side}`"
      >
        <span v-for="ch in col.chars" :key="ch">{{ ch }}</span>
      </div>
    </div>

    <!-- 装饰背景元素 -->
    <div class="bg-decor">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <!-- 顶部徽章 + 底部页脚（绝对定位，不参与单屏布局） -->
    <div class="hero-badge">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
      </svg>
      <span>声音家书</span>
    </div>

    <footer class="home-footer">
      <p>SayTopic - 声音家书，传递感恩</p>
    </footer>

    <!-- 单屏舞台 -->
    <div class="stage" :style="stageStyle">
      <div class="split" :class="`step-${step}`">
        <!-- 左栏：电话亭（始终存在） -->
        <section class="pane pane-left">
          <div class="pane-content pane-content-left">
            <AudioRecorder :key="recorderKey" @uploaded="onAudioUploaded" />
          </div>
        </section>

        <!-- 右栏：图片上传 / 明信片 -->
        <section class="pane pane-right">
          <Transition name="pane-swap" mode="out-in">
            <div v-if="step === 'image'" key="image" class="pane-content">
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
            </div>

            <div v-else-if="step === 'card'" key="card" class="pane-content">
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
                @printed="resetCreation"
              />
            </div>
          </Transition>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  position: fixed;
  inset: 0;
  overflow: hidden;
  padding: 0 16px;

  /* 布局旋钮：单栏内容宽度、两栏内容之间的空隙 */
  --pane-content-width: 560px;
  --pane-gap: 300px;
}

/* ===== 校园线稿背景（贴在页面底部，位于艺术字下层） ===== */
.bg-building {
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 100%;
  max-width: none;
  z-index: 0;
  pointer-events: none;
  user-select: none;
}

/* ===== 八字艺术字背景（左右两列竖排，蓝金渐变填充） ===== */
.bg-text {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
  user-select: none;
}

.bg-col {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
  font-family: var(--font-brush);
  font-size: clamp(96px, 7.2vw, 138px);
  line-height: 1.1;
  /* 一列四个字共用一条竖向渐变，形成从上到下蓝转金 */
  background: linear-gradient(180deg, #2F6FC4 0%, #4A90D9 38%, #A98A3C 72%, #C9A227 100%);
  -webkit-background-clip: text;
  background-clip: text;
  opacity: 0.42;
}

.bg-col span {
  color: transparent;
}

.bg-col-left {
  left: 2%;
  top: 7vh;
}

.bg-col-right {
  right: 2%;
  top: calc(7vh + 110px);
}

/* ===== 装饰背景 ===== */
.bg-decor {
  position: absolute;
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

/* ===== 顶部徽章 / 底部页脚 ===== */
.hero-badge {
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
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
}

.home-footer {
  position: absolute;
  bottom: 16px;
  left: 0;
  right: 0;
  z-index: 2;
  text-align: center;
  font-size: 12px;
  color: var(--neutral-400);
  font-family: var(--font-mono);
  letter-spacing: 1px;
}

/* ===== 单屏舞台 ===== */
.stage {
  position: absolute;
  inset: 0;
  z-index: 1;
  transform-origin: center;
}

.split {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

/* 阶段 0：电话亭居中，右栏隐藏。位移 = 内容半宽 + 间隙一半，保证电话亭落在屏幕正中 */
.split.step-record {
  transform: translateX(calc(var(--pane-content-width) / 2 + var(--pane-gap) / 2));
}

.split.step-image,
.split.step-card {
  transform: translateX(0);
}

.pane {
  width: 50%;
  height: 100%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  transition: opacity 0.4s ease, transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

/* 两栏内容各自向屏幕中间靠，中间只留 --pane-gap；整体仍关于屏幕中心对称 */
.pane-left {
  justify-content: flex-end;
  padding-right: calc(var(--pane-gap) / 2);
}

.pane-right {
  justify-content: flex-start;
  padding-left: calc(var(--pane-gap) / 2);
}

.split.step-record .pane-right {
  opacity: 0;
  transform: translateX(30%);
  pointer-events: none;
}

.pane-content {
  width: 100%;
  max-width: var(--pane-content-width);
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 电话亭内部尺寸自撑且带 margin auto，需要显式撑满容器，否则会缩成内容宽 */
.pane-content-left :deep(.recorder) {
  width: 100%;
  margin: 0;
}

/* 右栏内容切换：旧内容向左滑出，新内容从右滑入 */
.pane-swap-enter-active {
  animation: pane-in 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

.pane-swap-leave-active {
  animation: pane-out 0.3s ease-in;
}

@keyframes pane-in {
  0% {
    opacity: 0;
    transform: translateX(48px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pane-out {
  0% {
    opacity: 1;
    transform: translateX(0);
  }
  100% {
    opacity: 0;
    transform: translateX(-48px);
  }
}

/* ===== 分段 ===== */
.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.section-header.center {
  justify-content: center;
  text-align: center;
}

.section-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-100);
  border-radius: var(--radius-md);
  color: var(--primary-500);
  flex-shrink: 0;
}

.section-title {
  font-size: 17px;
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
.upload-options {
  display: flex;
  gap: 20px;
  /* 两侧卡片等高，视觉尺寸一致 */
  align-items: stretch;
}

.upload-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 16px;
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
  margin: 0 0 14px;
}

.upload-option-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: center;
  flex-shrink: 0;
  width: 40px;
}

.divider-text {
  font-size: 20px;
  font-weight: 600;
  color: #000;
}

.qr-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.qr-frame {
  width: 200px;
  height: 150px;
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
</style>
