<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import QRCode from 'qrcode'
import WaveformCanvas from './WaveformCanvas.vue'

const props = defineProps({
  audioUrl: { type: String, required: true },
  filename: { type: String, required: true },
  imageUrl: { type: String, default: '' },
})

const audioQrDataUrl = ref('')
const playUrl = ref('')
const showCard = ref(false)
const waveformRef = ref(null)

const fullImageUrl = computed(() => {
  if (!props.imageUrl) return ''
  return props.imageUrl.startsWith('http')
    ? props.imageUrl
    : `${window.location.origin}${props.imageUrl}`
})

function buildUrls() {
  const origin = window.location.origin
  playUrl.value = `${origin}/play/${props.filename}`
}

async function generateQrCodes() {
  try {
    if (playUrl.value) {
      audioQrDataUrl.value = await QRCode.toDataURL(playUrl.value, {
        width: 200,
        margin: 2,
        color: { dark: '#2D3748', light: '#ffffff' },
      })
    }
  } catch (e) {
    console.error('QR generation failed:', e)
  }
}

function print() {
  const canvas = waveformRef.value?.canvasRef
  const waveformDataUrl = canvas?.toDataURL('image/png') || ''
  const imageUrl = fullImageUrl.value

  const win = window.open('', '_blank', 'width=750,height=500')
  if (!win) {
    alert('请允许弹出窗口以预览明信片')
    return
  }

  win.document.write(`<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: #f0f0f0;
      font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
      padding: 20px;
      gap: 20px;
    }
    .postcard {
      width: 148mm;
      height: 100mm;
      position: relative;
      background: url('/mingxinpian.png') center/cover no-repeat;
      box-shadow: 0 4px 16px rgba(0,0,0,0.12);
      overflow: hidden;
    }
    .postcard-image {
      position: absolute;
      left: 12.2%;
      top: 15%;
      width: 28%;
      height: 53%;
      overflow: hidden;
      border: 2px dashed rgba(70,130,180,0.6);
      border-radius: 2px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .postcard-image img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .postcard-waveform {
      position: absolute;
      left: 11%;
      top: 67%;
      width: 28%;
      height: 16%;
    }
    .postcard-waveform img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 2px;
    }
    .postcard-qr {
      position: absolute;
      right: 22.5%;
      top: 33%;
      width: 18%;
      aspect-ratio: 1;
      background: white;
      border: 2px solid #e0e0e0;
      border-radius: 4px;
      padding: 4%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .postcard-qr img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    .print-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 10px 24px;
      background: linear-gradient(145deg, #5AB4D9, #4A90D9);
      color: white;
      border: none;
      border-radius: 9999px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(90,180,217,0.3);
    }
    .print-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(90,180,217,0.4);
    }
    @media print {
      body { background: white; padding: 0; gap: 0; }
      .print-btn { display: none !important; }
      .postcard { box-shadow: none; }
    }
    @page { size: 148mm 100mm; margin: 0; }
  </style>
</head>
<body>
  <div class="postcard">
    <div class="postcard-image">
      ${imageUrl ? `<img src="${imageUrl}" alt="关联图片" />` : ''}
    </div>
    <div class="postcard-waveform">
      ${waveformDataUrl ? `<img src="${waveformDataUrl}" alt="音频波形" />` : ''}
    </div>
    <div class="postcard-qr">
      <img src="${audioQrDataUrl.value}" alt="音频二维码" />
    </div>
  </div>
  <button class="print-btn" onclick="window.print()">
    打印明信片
  </button>
</body>
</html>`)
  win.document.close()
}

watch(() => props.filename, () => {
  buildUrls()
  generateQrCodes()
  setTimeout(() => { showCard.value = true }, 100)
})

onMounted(() => {
  buildUrls()
  generateQrCodes()
  setTimeout(() => { showCard.value = true }, 300)
})
</script>

<template>
  <div v-if="showCard" class="postcard-wrapper">
    <div class="postcard">
      <div v-if="fullImageUrl" class="postcard-image">
        <img :src="fullImageUrl" alt="关联图片" />
      </div>
      <div class="postcard-waveform">
        <WaveformCanvas ref="waveformRef" :audio-url="audioUrl" :height="80" :width="400" color-theme="primary" />
      </div>
      <div class="postcard-qr">
        <img v-if="audioQrDataUrl" :src="audioQrDataUrl" alt="音频二维码" />
      </div>
    </div>
    <button class="print-btn no-print" @click="print">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
        <polyline points="6 9 6 2 18 2 18 9"/>
        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
        <rect x="6" y="14" width="12" height="8"/>
      </svg>
      <span>打印明信片</span>
    </button>
  </div>
</template>

<style scoped>
.postcard-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.postcard {
  width: 148mm;
  height: 100mm;
  position: relative;
  background: url('/mingxinpian.png') center/cover no-repeat;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  overflow: hidden;
}

.postcard-image {
  position: absolute;
  left: 12.2%;
  top: 15%;
  width: 28%;
  height: 53%;
  overflow: hidden;
  border: 2px dashed rgba(70,130,180,0.6);
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.postcard-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.postcard-waveform {
  position: absolute;
  left: 11%;
  top: 67%;
  width: 28%;
  height: 16%;
  display: flex;
  align-items: center;
}

.postcard-waveform :deep(.waveform-canvas) {
  width: 100%;
  height: 100%;
}

.postcard-qr {
  position: absolute;
  right: 22.5%;
  top: 33%;
  width: 18%;
  aspect-ratio: 1;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  padding: 4%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.postcard-qr img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.print-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  padding: 10px 24px;
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

.print-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(90, 180, 217, 0.4);
}

@media print {
  .no-print { display: none !important; }
}
</style>
