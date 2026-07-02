<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  audioFilename: { type: String, required: true },
})

const emit = defineEmits(['captured'])

const videoRef = ref(null)
const canvasRef = ref(null)
const cameraReady = ref(false)
const cameraLoading = ref(true)
const cameraUnavailable = ref(false)
const capturing = ref(false)
const uploading = ref(false)
const error = ref('')

let stream = null

onMounted(async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
    })
    cameraLoading.value = false
    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
      cameraReady.value = true
    }
  } catch (e) {
    cameraUnavailable.value = true
    cameraLoading.value = false
    error.value = e.name === 'NotAllowedError'
      ? '请允许访问摄像头以使用拍照功能'
      : '无法访问摄像头，请检查设备'
  }
})

onUnmounted(() => {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop())
    stream = null
  }
})

async function capture() {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas) return

  capturing.value = true
  error.value = ''

  try {
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)

    canvas.toBlob(async (blob) => {
      if (!blob) {
        error.value = '拍照失败，请重试'
        capturing.value = false
        return
      }
      await uploadCapturedImage(blob)
    }, 'image/jpeg', 0.9)
  } catch {
    error.value = '拍照失败，请重试'
    capturing.value = false
  }
}

async function uploadCapturedImage(blob) {
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', blob, 'camera.jpg')
    formData.append('audio_filename', props.audioFilename)

    const res = await fetch('/api/upload-image', {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || '上传失败')
    }

    const data = await res.json()
    emit('captured', { url: data.url, filename: data.filename })
  } catch (e) {
    error.value = e.message || '上传失败，请重试'
  } finally {
    uploading.value = false
    capturing.value = false
  }
}
</script>

<template>
  <div class="camera-capture">
    <canvas ref="canvasRef" class="hidden-canvas"></canvas>

    <!-- 摄像头加载中 -->
    <div v-if="cameraLoading" class="camera-placeholder">
      <div class="spinner"></div>
      <p class="placeholder-text">正在启动摄像头...</p>
    </div>

    <!-- 摄像头不可用 -->
    <div v-else-if="cameraUnavailable" class="camera-placeholder">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36">
        <path d="M23 7l-7 5 7 5V7z"/>
        <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
        <line x1="2" y1="2" x2="22" y2="22" stroke-width="2"/>
      </svg>
      <p class="placeholder-text">{{ error }}</p>
    </div>

    <!-- 摄像头就绪 -->
    <template v-else>
      <div class="camera-preview">
        <video ref="videoRef" autoplay playsinline muted></video>
      </div>

      <button
        class="capture-btn"
        :disabled="capturing || uploading"
        @click="capture"
      >
        <svg v-if="!capturing && !uploading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        <span v-if="capturing && !uploading">正在拍照...</span>
        <span v-else-if="uploading">正在上传...</span>
        <span v-else>拍照</span>
      </button>

      <p v-if="error" class="capture-error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        {{ error }}
      </p>
    </template>
  </div>
</template>

<style scoped>
.camera-capture {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.hidden-canvas {
  display: none;
}

.camera-preview {
  width: 200px;
  height: 150px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 2px solid var(--primary-200);
  background: #000;
}

.camera-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.camera-placeholder {
  width: 200px;
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: var(--neutral-100);
  border: 2px dashed var(--neutral-300);
  border-radius: var(--radius-md);
  color: var(--neutral-400);
}

.placeholder-text {
  font-size: 13px;
  margin: 0;
  text-align: center;
  padding: 0 12px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--neutral-200);
  border-top-color: var(--primary-400);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.capture-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 28px;
  background: linear-gradient(145deg, var(--primary-400), var(--primary-600));
  color: white;
  border: none;
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(90, 180, 217, 0.3);
  transition: all 0.3s;
}

.capture-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(90, 180, 217, 0.4);
}

.capture-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.capture-error {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--accent-red);
  font-size: 13px;
  margin: 0;
}
</style>
