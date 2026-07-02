<script setup>
import { ref } from 'vue'

const emit = defineEmits(['uploaded'])

const uploading = ref(false)
const error = ref('')
const previewUrl = ref('')
const selectedFile = ref(null)

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

    const res = await fetch('/api/upload-image', {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Upload failed')
    }

    const data = await res.json()
    emit('uploaded', { url: data.url, filename: data.filename })
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
}
</script>

<template>
  <div class="image-uploader">
    <div
      class="upload-area"
      @drop="handleDrop"
      @dragover="handleDragOver"
    >
      <div v-if="!previewUrl" class="upload-prompt">
        <input
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/webp"
          @change="handleFileSelect"
          class="file-input"
          id="image-input"
        />
        <label for="image-input" class="upload-label">
          <div class="upload-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
          </div>
          <span class="upload-text">选择图片或拖拽到此处</span>
          <span class="format-hint">支持 JPG、PNG、WebP，最大 10MB</span>
        </label>
      </div>

      <div v-else class="preview-container">
        <div class="preview-frame">
          <img :src="previewUrl" alt="预览" class="preview-image" />
        </div>
        <div class="preview-actions">
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
    </div>

    <p v-if="error" class="error-message">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.image-uploader {
  width: 100%;
}

.upload-area {
  border: 2px dashed var(--primary-300);
  border-radius: var(--radius-md);
  padding: 32px 20px;
  text-align: center;
  transition: all 0.3s;
  background: rgba(232, 244, 252, 0.3);
}

.upload-area:hover {
  border-color: var(--primary-400);
  background: rgba(232, 244, 252, 0.5);
}

.upload-prompt {
  position: relative;
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
  gap: 10px;
  cursor: pointer;
}

.upload-icon {
  width: 64px;
  height: 64px;
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
  font-size: 15px;
  font-weight: 500;
  color: var(--neutral-600);
}

.format-hint {
  font-size: 12px;
  color: var(--neutral-400);
}

.preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.preview-frame {
  width: 200px;
  height: 200px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 3px solid white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-actions {
  display: flex;
  gap: 12px;
}

.upload-btn,
.reset-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border: none;
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-btn {
  background: linear-gradient(145deg, var(--primary-400), var(--primary-600));
  color: white;
  box-shadow: 0 4px 12px rgba(90, 180, 217, 0.3);
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(90, 180, 217, 0.4);
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

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--accent-red);
  margin-top: 12px;
  font-size: 13px;
}
</style>
