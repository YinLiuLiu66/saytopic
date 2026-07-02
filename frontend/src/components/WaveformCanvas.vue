<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  audioUrl: { type: String, required: true },
  height: { type: Number, default: 120 },
  width: { type: Number, default: 400 },
  colorTheme: { type: String, default: 'primary' },
})

const canvasRef = ref(null)
let audioContext = null

const themes = {
  primary: {
    line: '#5AB4D9',
    fill: 'rgba(168, 216, 234, 0.15)',
    bg: 'rgba(232, 244, 252, 0.3)',
  },
  coral: {
    line: '#FC8181',
    fill: 'rgba(252, 129, 129, 0.15)',
    bg: 'rgba(254, 215, 215, 0.3)',
  },
}

function getTheme() {
  return themes[props.colorTheme] || themes.primary
}

async function draw() {
  const canvas = canvasRef.value
  if (!canvas || !props.audioUrl) return

  canvas.width = props.width
  canvas.height = props.height

  try {
    const response = await fetch(props.audioUrl)
    const arrayBuffer = await response.arrayBuffer()

    if (audioContext) {
      audioContext.close()
    }
    audioContext = new AudioContext()
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

    const ctx = canvas.getContext('2d')
    const { width, height } = canvas
    const data = audioBuffer.getChannelData(0)
    const step = Math.ceil(data.length / width)
    const amp = height / 2
    const theme = getTheme()

    ctx.clearRect(0, 0, width, height)

    // 背景填充
    ctx.fillStyle = theme.bg
    ctx.fillRect(0, 0, width, height)

    // 中线
    ctx.beginPath()
    ctx.strokeStyle = 'rgba(168, 216, 234, 0.2)'
    ctx.lineWidth = 1
    ctx.setLineDash([4, 4])
    ctx.moveTo(0, amp)
    ctx.lineTo(width, amp)
    ctx.stroke()
    ctx.setLineDash([])

    // 波形填充区域
    ctx.beginPath()
    ctx.moveTo(0, amp)
    for (let i = 0; i < width; i++) {
      let min = 1.0
      let max = -1.0
      for (let j = 0; j < step; j++) {
        const idx = i * step + j
        if (idx < data.length) {
          const val = data[idx]
          if (val < min) min = val
          if (val > max) max = val
        }
      }
      const y1 = amp + min * amp * 0.85
      ctx.lineTo(i, y1)
    }
    ctx.lineTo(width, amp)
    for (let i = width - 1; i >= 0; i--) {
      let max = -1.0
      for (let j = 0; j < step; j++) {
        const idx = i * step + j
        if (idx < data.length) {
          const val = data[idx]
          if (val > max) max = val
        }
      }
      const y2 = amp + max * amp * 0.85
      ctx.lineTo(i, y2)
    }
    ctx.closePath()
    ctx.fillStyle = theme.fill
    ctx.fill()

    // 波形线条
    ctx.beginPath()
    ctx.strokeStyle = theme.line
    ctx.lineWidth = 1.5
    ctx.lineJoin = 'round'

    for (let i = 0; i < width; i++) {
      let min = 1.0
      let max = -1.0
      for (let j = 0; j < step; j++) {
        const idx = i * step + j
        if (idx < data.length) {
          const val = data[idx]
          if (val < min) min = val
          if (val > max) max = val
        }
      }
      const y1 = amp + min * amp * 0.85
      const y2 = amp + max * amp * 0.85
      ctx.moveTo(i, y1)
      ctx.lineTo(i, y2)
    }
    ctx.stroke()
  } catch (e) {
    console.error('Failed to draw waveform:', e)
  }
}

watch(() => props.audioUrl, () => {
  if (props.audioUrl) setTimeout(draw, 100)
})

onMounted(() => {
  if (props.audioUrl) setTimeout(draw, 100)
})

onUnmounted(() => {
  if (audioContext) audioContext.close()
})

defineExpose({ canvasRef })
</script>

<template>
  <canvas ref="canvasRef" :width="width" :height="height" class="waveform-canvas" />
</template>

<style scoped>
.waveform-canvas {
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-sm, 8px);
}
</style>
