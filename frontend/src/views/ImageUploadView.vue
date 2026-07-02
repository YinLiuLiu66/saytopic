<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const audioFilename = computed(() => route.params.audioFilename)

const uploading = ref(false)
const uploaded = ref(false)
const error = ref('')
const previewUrl = ref('')
const selectedFile = ref(null)
const showPage = ref(false)

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    validateAndPreview(file)
  }
}

function handleDrop(event) {
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndPreview(file)
  }
}

function handleDragOver(event) {
  event.preventDefault()
}

function validateAndPreview(file) {
  error.value = ''

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    error.value = '支持的格式：JPG、PNG、WebP'
    return
  }

  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    error.value = '图片大小不能超过10MB'
    return
  }

  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

async function uploadImage() {
  if (!selectedFile.value) return

  error.value = ''
  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('audio_filename', audioFilename.value)

    const res = await fetch('/api/upload-image', {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Upload failed')
    }

    uploaded.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
  }
}

function reset() {
  selectedFile.value = null
  previewUrl.value = ''
  error.value = ''
  uploaded.value = false
}

onMounted(() => {
  setTimeout(() => { showPage.value = true }, 100)
})
</script>

<template>
  <div class="image-upload-view">
    <!-- 装饰背景 -->
    <div class="bg-decor">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
    </div>

    <Transition name="page-enter">
      <main v-if="showPage" class="upload-main">
        <!-- 品牌标识 -->
        <div class="brand-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
          <span>SayTopic</span>
        </div>

        <!-- 上传卡片 -->
        <div class="upload-card">
          <!-- 头部 -->
          <div class="card-header">
            <h1 class="card-title">上传照片</h1>
            <p class="card-subtitle">为这段声音配上专属图片</p>
          </div>

          <!-- 上传内容 -->
          <div class="card-body">
            <div v-if="!uploaded" class="upload-content">
              <!-- 上传区域 -->
              <div
                v-if="!previewUrl"
                class="upload-area"
                @drop="handleDrop"
                @dragover="handleDragOver"
              >
                <input
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  capture="environment"
                  @change="handleFileSelect"
                  class="file-input"
                  id="mobile-image-input"
                />
                <label for="mobile-image-input" class="upload-label">
                  <div class="upload-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="32" height="32">
                      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                      <circle cx="12" cy="13" r="4"/>
                    </svg>
                  </div>
                  <span class="upload-text">拍照或选择图片</span>
                  <span class="upload-hint">支持 JPG、PNG、WebP，最大 10MB</span>
                </label>
              </div>

              <!-- 预览区域 -->
              <div v-else class="preview-section">
                <div class="preview-frame">
                  <img :src="previewUrl" alt="预览" class="preview-image" />
                </div>
                <div class="action-buttons">
                  <button
                    class="upload-btn"
                    :disabled="uploading"
                    @click="uploadImage"
                  >
                    <svg v-if="!uploading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <span>{{ uploading ? '上传中...' : '确认上传' }}</span>
                  </button>
                  <button
                    class="reset-btn"
                    :disabled="uploading"
                    @click="reset"
                  >
                    重新选择
                  </button>
                </div>
              </div>

              <!-- 错误信息 -->
              <p v-if="error" class="error-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                {{ error }}
              </p>
            </div>

            <!-- 成功状态 -->
            <div v-else class="success-section">
              <div class="success-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="36" height="36">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
              <h3 class="success-title">上传成功！</h3>
              <p class="success-desc">图片已成功关联到声音明信片</p>
              <button class="reset-btn" @click="reset">
                上传另一张图片
              </button>
            </div>
          </div>

          <!-- 底部 -->
          <div class="card-footer">
            <p class="footer-text">听见心声 · 传递感恩</p>
          </div>
        </div>
      </main>
    </Transition>
  </div>
</template>

<style scoped>
.image-upload-view {
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

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.06;
}

.bg-circle-1 {
  width: 400px;
  height: 400px;
  background: var(--primary-400);
  top: -100px;
  right: -80px;
  animation: float-slow 20s ease-in-out infinite;
}

.bg-circle-2 {
  width: 300px;
  height: 300px;
  background: var(--accent-coral);
  bottom: -50px;
  left: -80px;
  animation: float-slow 15s ease-in-out infinite reverse;
}

@keyframes float-slow {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(15px, -10px); }
}

/* ===== 页面过渡 ===== */
.page-enter-enter-active {
  animation: page-in 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes page-in {
  0% {
    opacity: 0;
    transform: translateY(30px) scale(0.97);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ===== 主内容 ===== */
.upload-main {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 480px;
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

/* ===== 上传卡片 ===== */
.upload-card {
  width: 100%;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--primary-200);
}

/* 卡片头部 */
.card-header {
  padding: 28px 24px 20px;
  text-align: center;
  background: linear-gradient(135deg, var(--primary-100), var(--primary-200));
  border-bottom: 1px dashed var(--primary-300);
}

.card-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--neutral-700);
  margin: 0 0 4px;
}

.card-subtitle {
  font-size: 13px;
  color: var(--neutral-500);
  margin: 0;
}

/* 卡片内容 */
.card-body {
  padding: 24px;
}

/* 上传区域 */
.upload-area {
  position: relative;
  border: 2px dashed var(--primary-300);
  border-radius: var(--radius-md);
  padding: 40px 20px;
  text-align: center;
  transition: all 0.3s;
  background: rgba(232, 244, 252, 0.2);
}

.upload-area:hover {
  border-color: var(--primary-400);
  background: rgba(232, 244, 252, 0.4);
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.upload-icon {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-md);
  background: var(--primary-100);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-400);
  transition: all 0.3s;
}

.upload-area:hover .upload-icon {
  background: var(--primary-200);
  color: var(--primary-500);
  transform: translateY(-2px);
}

.upload-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-600);
}

.upload-hint {
  font-size: 12px;
  color: var(--neutral-400);
}

/* 预览区域 */
.preview-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.preview-frame {
  width: 100%;
  max-width: 300px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 3px solid white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.preview-image {
  width: 100%;
  height: auto;
  display: block;
}

.action-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: center;
}

/* 按钮 */
.upload-btn,
.reset-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: var(--radius-full);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-btn {
  background: linear-gradient(145deg, var(--primary-400), var(--primary-600));
  color: white;
  box-shadow: 0 4px 14px rgba(90, 180, 217, 0.3);
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(90, 180, 217, 0.4);
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

/* 错误信息 */
.error-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--accent-red);
  margin: 16px 0 0;
  font-size: 13px;
}

/* 成功状态 */
.success-section {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(145deg, #48BB78, #38A169);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 4px 20px rgba(72, 187, 120, 0.3);
  animation: success-pop 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes success-pop {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.success-title {
  font-size: 20px;
  font-weight: 600;
  color: #38A169;
  margin: 0 0 8px;
}

.success-desc {
  font-size: 14px;
  color: var(--neutral-500);
  margin: 0 0 24px;
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

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .card-header {
    padding: 20px 16px 16px;
  }

  .card-body {
    padding: 20px 16px;
  }

  .upload-area {
    padding: 32px 16px;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
