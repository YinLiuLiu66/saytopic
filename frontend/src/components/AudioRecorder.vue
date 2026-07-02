<script setup>
import { ref, onUnmounted, computed } from 'vue'

const emit = defineEmits(['uploaded'])

const recording = ref(false)
const uploading = ref(false)
const recorded = ref(false)
const error = ref('')
const duration = ref(0)
const audioBlob = ref(null)
const audioUrl = ref('')
let mediaRecorder = null
let audioChunks = []
let timerInterval = null
let stream = null

const timeDisplay = computed(() => {
  const mins = Math.floor(duration.value / 60)
  const secs = duration.value % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

const progressPercent = computed(() => {
  return Math.min((duration.value / 60) * 100, 100)
})

const isOverLimit = computed(() => duration.value >= 60)

async function startRecording() {
  error.value = ''
  audioChunks = []
  duration.value = 0
  recorded.value = false
  audioBlob.value = null
  audioUrl.value = ''

  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: getSupportedMimeType()
    })

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        audioChunks.push(e.data)
      }
    }

    mediaRecorder.onstop = () => {
      const mimeType = mediaRecorder.mimeType
      audioBlob.value = new Blob(audioChunks, { type: mimeType })
      audioUrl.value = URL.createObjectURL(audioBlob.value)
      recorded.value = true
      clearInterval(timerInterval)
      stopStream()
    }

    mediaRecorder.start()
    recording.value = true

    timerInterval = setInterval(() => {
      duration.value++
      if (duration.value >= 60) {
        stopRecording()
      }
    }, 1000)
  } catch (e) {
    error.value = '无法访问麦克风，请检查权限设置'
    console.error('Recording error:', e)
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    recording.value = false
  }
}

function stopStream() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
}

function getSupportedMimeType() {
  const types = [
    'audio/mp4',
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/ogg',
  ]
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type
    }
  }
  return ''
}

function getExtension() {
  const mimeType = mediaRecorder?.mimeType || ''
  if (mimeType.includes('webm')) return '.webm'
  if (mimeType.includes('ogg')) return '.ogg'
  if (mimeType.includes('mp4')) return '.m4a'
  return '.webm'
}

async function uploadRecording() {
  if (!audioBlob.value) return

  error.value = ''
  uploading.value = true

  try {
    const ext = getExtension()
    const filename = `recording${ext}`
    const file = new File([audioBlob.value], filename, { type: audioBlob.value.type })

    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.error || 'Upload failed')
    }

    const data = await res.json()
    emit('uploaded', { url: data.url, filename: data.filename })
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
  }
}

function resetRecording() {
  recorded.value = false
  audioBlob.value = null
  audioUrl.value = ''
  duration.value = 0
  error.value = ''
}

onUnmounted(() => {
  stopStream()
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<template>
  <div class="recorder">
    <!-- 电话亭顶部装饰 -->
    <div class="booth-top">
      <div class="booth-antenna"></div>
      <div class="booth-dome">
        <span class="dome-label">SAY TOPIC</span>
      </div>
    </div>

    <!-- 电话亭主体 -->
    <div class="booth-body">
      <!-- 状态指示灯 -->
      <div class="status-lights">
        <div class="light" :class="{ active: recording }"></div>
        <div class="light-label">
          {{ recording ? '录音中...' : recorded ? '录音完成' : '等待录音' }}
        </div>
      </div>

      <!-- 视觉区域 -->
      <div class="recorder-visual">
        <!-- 录音中的脉冲动画 -->
        <div v-if="recording" class="pulse-container">
          <div class="pulse-ring"></div>
          <div class="pulse-ring delay-1"></div>
          <div class="pulse-ring delay-2"></div>
          <div class="mic-icon recording">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
          </div>
        </div>

        <!-- 等待状态 -->
        <div v-else-if="!recorded" class="idle-visual">
          <div class="mic-icon idle">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
          </div>
          <p class="idle-hint">按下按钮，录下你的感恩之声</p>
          <p class="idle-duration">时长 30-60 秒</p>
        </div>

        <!-- 录音完成 - 回放 -->
        <div v-else class="playback-container">
          <div class="playback-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 18V12.5L4.5 18H3V6h1.5L9 11.5V6h1.5v12H9zm7.5-6a4.5 4.5 0 0 1-4.5 4.5V6a4.5 4.5 0 0 1 4.5 4.5z"/>
            </svg>
          </div>
          <audio :src="audioUrl" controls class="audio-preview"></audio>
        </div>
      </div>

      <!-- 录音计时器 -->
      <div v-if="recording || recorded" class="timer-section">
        <div class="timer-display">{{ timeDisplay }}</div>
        <div class="timer-bar">
          <div class="timer-progress" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <div class="timer-limit">/ 01:00</div>
      </div>

      <!-- 控制按钮 -->
      <div class="recorder-controls">
        <template v-if="!recorded">
          <button
            v-if="!recording"
            class="record-btn"
            @click="startRecording"
          >
            <span class="btn-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="8"/>
              </svg>
            </span>
            <span class="btn-text">开始录音</span>
          </button>
          <button
            v-else
            class="stop-btn"
            @click="stopRecording"
          >
            <span class="btn-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12" rx="2"/>
              </svg>
            </span>
            <span class="btn-text">停止录音</span>
          </button>
        </template>
        <template v-else>
          <button
            class="upload-btn"
            :disabled="uploading"
            @click="uploadRecording"
          >
            <span class="btn-icon">
              <svg v-if="!uploading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <svg v-else class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
            </span>
            <span class="btn-text">{{ uploading ? '上传中...' : '生成明信片' }}</span>
          </button>
          <button
            class="reset-btn"
            :disabled="uploading"
            @click="resetRecording"
          >
            <span class="btn-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="1 4 1 10 7 10"/>
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
              </svg>
            </span>
            <span class="btn-text">重新录音</span>
          </button>
        </template>
      </div>

      <!-- 错误信息 -->
      <p v-if="error" class="recorder-error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        {{ error }}
      </p>
    </div>

    <!-- 电话亭底座 -->
    <div class="booth-base">
      <div class="base-detail"></div>
    </div>
  </div>
</template>

<style scoped>
.recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 420px;
  margin: 0 auto;
  position: relative;
}

/* ===== 电话亭顶部 ===== */
.booth-top {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 2;
}

.booth-antenna {
  width: 4px;
  height: 24px;
  background: linear-gradient(to bottom, var(--primary-400), var(--primary-300));
  border-radius: 2px;
  position: relative;
}

.booth-antenna::after {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 10px;
  height: 10px;
  background: var(--primary-400);
  border-radius: 50%;
}

.booth-dome {
  width: 100%;
  padding: 10px 0;
  background: linear-gradient(180deg, var(--primary-400), var(--primary-500));
  border-radius: 40px 40px 0 0;
  text-align: center;
  position: relative;
  margin-top: -2px;
}

.dome-label {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: white;
  letter-spacing: 6px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* ===== 电话亭主体 ===== */
.booth-body {
  width: 100%;
  background: var(--bg-card);
  border: 3px solid var(--primary-300);
  border-top: none;
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  position: relative;
  box-shadow: var(--shadow-lg);
}

/* 玻璃纹理效果 */
.booth-body::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(168, 216, 234, 0.03) 2px,
      rgba(168, 216, 234, 0.03) 4px
    );
  pointer-events: none;
  border-radius: 0 0 16px 16px;
}

/* ===== 状态指示灯 ===== */
.status-lights {
  display: flex;
  align-items: center;
  gap: 10px;
}

.light {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--neutral-300);
  transition: all 0.3s;
}

.light.active {
  background: var(--accent-red);
  box-shadow: 0 0 8px rgba(229, 62, 62, 0.6);
  animation: led-blink 1s ease-in-out infinite;
}

@keyframes led-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.light-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--neutral-500);
  letter-spacing: 1px;
}

/* ===== 视觉区域 ===== */
.recorder-visual {
  width: 100%;
  min-height: 140px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 录音中脉冲 */
.pulse-container {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pulse-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(252, 129, 129, 0.2);
  animation: pulse-expand 2s ease-out infinite;
}

.pulse-ring.delay-1 { animation-delay: 0.6s; }
.pulse-ring.delay-2 { animation-delay: 1.2s; }

@keyframes pulse-expand {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(2.5); opacity: 0; }
}

.mic-icon {
  width: 48px;
  height: 48px;
  color: var(--primary-500);
  z-index: 1;
}

.mic-icon.idle {
  width: 64px;
  height: 64px;
  color: var(--primary-400);
  animation: mic-float 3s ease-in-out infinite;
}

.mic-icon.recording {
  color: var(--accent-red);
  animation: mic-pulse 1s ease-in-out infinite;
}

@keyframes mic-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes mic-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.idle-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.idle-hint {
  font-size: 15px;
  color: var(--neutral-600);
  font-weight: 500;
}

.idle-duration {
  font-size: 12px;
  color: var(--neutral-400);
  font-family: var(--font-mono);
  letter-spacing: 1px;
}

/* 回放区域 */
.playback-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.playback-icon {
  width: 40px;
  height: 40px;
  color: var(--primary-500);
}

.audio-preview {
  width: 100%;
  max-width: 340px;
  height: 40px;
  border-radius: 20px;
}

/* ===== 计时器 ===== */
.timer-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.timer-display {
  font-family: var(--font-mono);
  font-size: 42px;
  font-weight: 700;
  color: var(--primary-600);
  letter-spacing: 4px;
  text-shadow: 0 2px 4px rgba(74, 144, 217, 0.15);
}

.timer-bar {
  width: 100%;
  max-width: 280px;
  height: 4px;
  background: var(--neutral-200);
  border-radius: 2px;
  overflow: hidden;
}

.timer-progress {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-400), var(--accent-coral));
  border-radius: 2px;
  transition: width 1s linear;
}

.timer-limit {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--neutral-400);
}

/* ===== 控制按钮 ===== */
.recorder-controls {
  display: flex;
  gap: 16px;
  width: 100%;
  justify-content: center;
}

.record-btn,
.stop-btn,
.upload-btn,
.reset-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border: none;
  border-radius: var(--radius-full);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.btn-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon svg {
  width: 100%;
  height: 100%;
}

.record-btn {
  background: linear-gradient(145deg, var(--accent-coral), var(--accent-red));
  color: white;
  box-shadow: 0 4px 16px rgba(229, 62, 62, 0.35);
}

.record-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(229, 62, 62, 0.45);
}

.record-btn:active {
  transform: translateY(0);
}

.stop-btn {
  background: linear-gradient(145deg, var(--neutral-600), var(--neutral-700));
  color: white;
  box-shadow: 0 4px 16px rgba(45, 55, 72, 0.3);
}

.stop-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(45, 55, 72, 0.4);
}

.upload-btn {
  background: linear-gradient(145deg, var(--primary-400), var(--primary-600));
  color: white;
  box-shadow: 0 4px 16px rgba(90, 180, 217, 0.35);
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(90, 180, 217, 0.45);
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.reset-btn {
  background: var(--neutral-100);
  color: var(--neutral-600);
  border: 1.5px solid var(--neutral-200);
}

.reset-btn:hover:not(:disabled) {
  background: var(--neutral-200);
  transform: translateY(-1px);
}

.reset-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 旋转动画 */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ===== 错误信息 ===== */
.recorder-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--accent-red);
  font-size: 13px;
  padding: 10px 16px;
  background: rgba(229, 62, 62, 0.06);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(229, 62, 62, 0.15);
}

/* ===== 电话亭底座 ===== */
.booth-base {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.base-detail {
  width: 100%;
  height: 12px;
  background: linear-gradient(180deg, var(--primary-300), var(--primary-200));
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  margin-top: -2px;
}

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .booth-body {
    padding: 24px 16px;
  }

  .dome-label {
    font-size: 15px;
    letter-spacing: 4px;
  }

  .timer-display {
    font-size: 32px;
  }

  .record-btn,
  .stop-btn,
  .upload-btn,
  .reset-btn {
    padding: 12px 20px;
    font-size: 14px;
  }
}
</style>
