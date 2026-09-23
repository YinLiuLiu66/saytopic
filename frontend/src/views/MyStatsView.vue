<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SiteFooter from '../components/SiteFooter.vue'

const router = useRouter()
const username = ref(localStorage.getItem('saytopic_username') || '')
const usernameInput = ref('')
const listenedCount = ref(0)
const loading = ref(false)
const error = ref('')
const credentialUrl = ref('')

async function loadStats() {
  if (!username.value) return
  loading.value = true
  error.value = ''

  try {
    const encodedUsername = encodeURIComponent(username.value)
    const res = await fetch(`/api/listening-stats?username=${encodedUsername}`)
    if (!res.ok) throw new Error('无法加载统计')
    listenedCount.value = (await res.json()).listened_count
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function saveUsername() {
  const value = usernameInput.value.trim()
  if (!value || value.length > 40) return
  username.value = value
  usernameInput.value = ''
  credentialUrl.value = ''
  localStorage.setItem('saytopic_username', value)
  loadStats()
}

function switchUsername() {
  localStorage.removeItem('saytopic_username')
  username.value = ''
  listenedCount.value = 0
  credentialUrl.value = ''
}

function generateCredential() {
  const canvas = document.createElement('canvas')
  canvas.width = 1080
  canvas.height = 1080
  const context = canvas.getContext('2d')

  const gradient = context.createLinearGradient(0, 0, 1080, 1080)
  gradient.addColorStop(0, '#E8F4FC')
  gradient.addColorStop(1, '#C5E4F7')
  context.fillStyle = gradient
  context.fillRect(0, 0, 1080, 1080)

  context.strokeStyle = '#5AB4D9'
  context.lineWidth = 12
  context.strokeRect(72, 72, 936, 936)

  context.fillStyle = '#2D3748'
  context.textAlign = 'center'
  context.textBaseline = 'middle'
  context.font = "700 88px 'Noto Sans SC', sans-serif"
  context.fillText(username.value, 540, 430, 860)
  context.font = "600 76px 'Noto Sans SC', sans-serif"
  context.fillText(`已听 ${listenedCount.value} 条录音`, 540, 640, 860)

  credentialUrl.value = canvas.toDataURL('image/png')
}

onMounted(loadStats)
</script>

<template>
  <main class="stats-page">
    <button class="back-button" type="button" @click="router.back()">← 返回播放页</button>

    <section v-if="!username" class="stats-card">
      <h1>我的统计</h1>
      <p>输入用户名查看已听数量</p>
      <form class="username-form" @submit.prevent="saveUsername">
        <input
          v-model="usernameInput"
          maxlength="40"
          placeholder="请输入用户名"
          aria-label="用户名"
          required
        />
        <button type="submit">确认</button>
      </form>
    </section>

    <section v-else class="stats-card">
      <div class="stats-header">
        <div>
          <h1>我的统计</h1>
          <p>用户名：{{ username }}</p>
        </div>
        <button class="switch-button" type="button" @click="switchUsername">切换用户名</button>
      </div>

      <p v-if="loading" class="status">正在加载...</p>
      <p v-else-if="error" class="status error">{{ error }}</p>
      <template v-else>
        <p class="count">已听 <strong>{{ listenedCount }}</strong> 条录音</p>
        <button class="generate-button" type="button" @click="generateCredential">
          生成凭证图片
        </button>
      </template>
    </section>

    <section v-if="credentialUrl" class="credential-section">
      <p>长按下方图片保存到手机相册</p>
      <img :src="credentialUrl" :alt="`${username} 已听 ${listenedCount} 条录音`" />
    </section>

    <SiteFooter />
  </main>
</template>

<style scoped>
.stats-page {
  width: min(640px, calc(100% - 32px));
  margin: 0 auto;
  padding: 32px 0 64px;
}

.back-button,
.switch-button {
  border: 0;
  background: transparent;
  color: var(--primary-600);
}

.stats-card,
.credential-section {
  margin-top: 20px;
  padding: 24px;
  border: 1px solid var(--primary-200);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--shadow-sm);
}

.stats-card h1 {
  margin: 0;
  color: var(--neutral-700);
}

.stats-card p {
  color: var(--neutral-500);
}

.stats-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.username-form {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.username-form input {
  min-width: 0;
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--primary-300);
  border-radius: var(--radius-md);
}

.username-form button,
.generate-button {
  padding: 10px 18px;
  border: 0;
  border-radius: var(--radius-full);
  background: var(--primary-500);
  color: white;
}

.count {
  margin: 32px 0;
  text-align: center;
  font-size: 24px;
}

.count strong {
  font-size: 48px;
  color: var(--primary-600);
}

.generate-button {
  display: block;
  margin: 0 auto;
}

.status,
.credential-section {
  text-align: center;
}

.error {
  color: var(--accent-red);
}

.credential-section img {
  display: block;
  width: 100%;
  margin-top: 16px;
  border-radius: var(--radius-md);
  -webkit-touch-callout: default;
}

@media (max-width: 480px) {
  .stats-header,
  .username-form {
    flex-direction: column;
  }

  .username-form input,
  .username-form button {
    width: 100%;
  }
}
</style>
