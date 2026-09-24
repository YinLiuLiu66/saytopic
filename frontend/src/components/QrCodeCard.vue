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

// 明信片各区域在底图中的位置（百分比），HTML 预览与打印 PDF 共用这一份坐标
const CARD_REGIONS = {
  photo: { left: 12.664, top: 20.833, width: 27.138, height: 45.037 },
  waveform: { left: 51.85, top: 65.2, width: 41.94, height: 10.4 },
  qr: { left: 56.59, top: 37.35, width: 17.38, height: 27.35 },
}

// 卡片宽度固定 148mm；高度不写死，按底图实际比例推得，保证打印不变形
const CARD_WIDTH_MM = 148
// 与 frontend/public/mingxinpian.jpg 的实际比例一致（2048 × 1360 ≈ 1.5059）；更换底图时须同步
const CARD_ASPECT = 2048 / 1360
const cardHeightMm = CARD_WIDTH_MM / CARD_ASPECT

function regionStyle(region) {
  return {
    left: `${region.left}%`,
    top: `${region.top}%`,
    width: `${region.width}%`,
    height: `${region.height}%`,
  }
}

function regionRect(region, width, height) {
  return {
    x: (region.left / 100) * width,
    y: (region.top / 100) * height,
    width: (region.width / 100) * width,
    height: (region.height / 100) * height,
  }
}

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
        width: 400,
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
      loadImage(`${window.location.origin}/mingxinpian.jpg`),
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
    const photoRect = regionRect(CARD_REGIONS.photo, width, height)
    const waveformRect = regionRect(CARD_REGIONS.waveform, width, height)
    const qrRect = regionRect(CARD_REGIONS.qr, width, height)
    // 二维码四周留出白边，保证静区不被底图灰块压到
    const qrPadding = qrRect.width * 0.04

    ctx.drawImage(background, 0, 0, width, height)
    if (photo) {
      // 完整显示照片，不裁切
      drawContain(ctx, photo, photoRect.x, photoRect.y, photoRect.width, photoRect.height)
    }
    drawContain(ctx, waveform, waveformRect.x, waveformRect.y, waveformRect.width, waveformRect.height)
    ctx.fillStyle = 'white'
    ctx.fillRect(qrRect.x, qrRect.y, qrRect.width, qrRect.height)
    drawContain(
      ctx,
      qr,
      qrRect.x + qrPadding,
      qrRect.y + qrPadding,
      qrRect.width - qrPadding * 2,
      qrRect.height - qrPadding * 2,
    )

    const { jsPDF } = await import('jspdf')
    // 页高按底图实际比例推得，避免打印时被拉伸（宽度固定 148mm）
    const pageHeight = (CARD_WIDTH_MM * background.naturalHeight) / background.naturalWidth
    const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: [CARD_WIDTH_MM, pageHeight] })
    pdf.addImage(canvas, 'PNG', 0, 0, CARD_WIDTH_MM, pageHeight)
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
    <div class="postcard" :style="{ height: `${cardHeightMm}mm` }">
      <div v-if="fullImageUrl" class="postcard-image" :style="regionStyle(CARD_REGIONS.photo)">
        <img :src="fullImageUrl" alt="关联图片" />
      </div>
      <div class="postcard-waveform" :style="regionStyle(CARD_REGIONS.waveform)">
        <WaveformCanvas ref="waveformRef" :audio-url="audioUrl" :height="141" :width="859" color-theme="card" />
      </div>
      <div class="postcard-qr" :style="regionStyle(CARD_REGIONS.qr)">
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
  position: relative;
  /* 底图直接拉满卡片；高度由脚本按底图实际比例给出，保证与打印 PDF 一致 */
  background: url('/mingxinpian.jpg') center/100% 100% no-repeat;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  overflow: hidden;
}

/* 三个区域的坐标统一来自脚本里的 CARD_REGIONS，避免与打印 PDF 出现两份参数 */
.postcard-image,
.postcard-waveform,
.postcard-qr {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 二维码区域画白底遮盖底图灰块，给二维码留出完整静区（与 PDF 一致的 4% 边距） */
.postcard-qr {
  background: #fff;
  padding: 4%;
}

.postcard-image img {
  width: 100%;
  height: 100%;
  /* 完整显示照片，不裁切 */
  object-fit: contain;
}

.postcard-waveform :deep(.waveform-canvas) {
  width: 100%;
  height: 100%;
  border-radius: 0;
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
