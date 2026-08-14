<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import QRCode from 'qrcode'
import WaveformCanvas from './WaveformCanvas.vue'

const emit = defineEmits(['printed'])

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

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = () => reject(new Error('图片加载失败'))
    image.src = url
  })
}

function drawCover(ctx, image, x, y, width, height) {
  const sourceWidth = image.naturalWidth || image.width
  const sourceHeight = image.naturalHeight || image.height
  const scale = Math.max(width / sourceWidth, height / sourceHeight)
  const cropWidth = width / scale
  const cropHeight = height / scale
  ctx.drawImage(
    image,
    (sourceWidth - cropWidth) / 2,
    (sourceHeight - cropHeight) / 2,
    cropWidth,
    cropHeight,
    x,
    y,
    width,
    height,
  )
}

function drawContain(ctx, image, x, y, width, height) {
  const sourceWidth = image.naturalWidth || image.width
  const sourceHeight = image.naturalHeight || image.height
  const scale = Math.min(width / sourceWidth, height / sourceHeight)
  const drawWidth = sourceWidth * scale
  const drawHeight = sourceHeight * scale
  ctx.drawImage(image, x + (width - drawWidth) / 2, y + (height - drawHeight) / 2, drawWidth, drawHeight)
}

async function print() {
  const win = window.open('', '_blank')
  if (!win) {
    alert('请允许弹出窗口以打开打印版 PDF')
    return
  }

  win.document.write('<title>正在生成打印版 PDF</title><p>正在生成打印版 PDF…</p>')
  win.document.close()

  try {
    if (!audioQrDataUrl.value) await generateQrCodes()

    const waveform = waveformRef.value?.canvasRef
    if (!waveform || !audioQrDataUrl.value) throw new Error('明信片内容尚未准备好')

    const [background, qr, photo] = await Promise.all([
      loadImage(`${window.location.origin}/mingxinpian.png`),
      loadImage(audioQrDataUrl.value),
      fullImageUrl.value ? loadImage(fullImageUrl.value) : Promise.resolve(null),
    ])
    const canvas = document.createElement('canvas')
    canvas.width = background.naturalWidth
    canvas.height = background.naturalHeight
    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('无法生成明信片')

    const width = canvas.width
    const height = canvas.height
    const photoX = width * 0.122
    const photoY = height * 0.15
    const photoWidth = width * 0.28
    const photoHeight = height * 0.53
    const waveformX = width * 0.11
    const waveformY = height * 0.67
    const waveformWidth = width * 0.28
    const waveformHeight = height * 0.16
    const qrWidth = width * 0.18
    const qrX = width - width * 0.225 - qrWidth
    const qrY = height * 0.33
    const qrPadding = width * 0.04

    ctx.drawImage(background, 0, 0, width, height)
    if (photo) drawCover(ctx, photo, photoX, photoY, photoWidth, photoHeight)
    ctx.save()
    ctx.strokeStyle = 'rgba(70,130,180,0.6)'
    ctx.lineWidth = width * 0.0036
    ctx.setLineDash([width * 0.014, width * 0.009])
    ctx.strokeRect(photoX, photoY, photoWidth, photoHeight)
    ctx.restore()
    drawContain(ctx, waveform, waveformX, waveformY, waveformWidth, waveformHeight)
    ctx.fillStyle = 'white'
    ctx.fillRect(qrX, qrY, qrWidth, qrWidth)
    ctx.strokeStyle = '#e0e0e0'
    ctx.lineWidth = width * 0.0036
    ctx.strokeRect(qrX, qrY, qrWidth, qrWidth)
    drawContain(ctx, qr, qrX + qrPadding, qrY + qrPadding, qrWidth - qrPadding * 2, qrWidth - qrPadding * 2)

    const { jsPDF } = await import('jspdf')
    const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: [148, 100] })
    pdf.addImage(canvas, 'PNG', 0, 0, 148, 100)
    win.location.href = pdf.output('bloburl')
    emit('printed')
  } catch (error) {
    console.error('Failed to generate postcard PDF:', error)
    win.close()
    alert('生成打印版 PDF 失败，请重试')
  }
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
