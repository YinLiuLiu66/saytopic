<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref(localStorage.getItem('saytopic_username') || '')
const recordings = ref([])
const loading = ref(false)
const error = ref('')

async function loadRecordings() {
  if (!username.value) return
  loading.value = true

  try {
    const res = await fetch(`/api/recordings?owner_name=${encodeURIComponent(username.value)}`)
    if (!res.ok) throw new Error('无法加载录音')
    recordings.value = (await res.json()).recordings
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function switchUsername() {
  localStorage.removeItem('saytopic_username')
  router.push('/')
}

function formatDate(value) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadRecordings)
</script>

<template>
  <main class="mine">
    <header class="mine-header">
      <RouterLink class="back-link" to="/">← 返回录音页</RouterLink>
      <h1>我的录音</h1>
      <p v-if="username">用户名：{{ username }}</p>
    </header>

    <section v-if="!username" class="empty-card">
      <p>请先返回首页输入用户名。</p>
      <RouterLink class="primary-link" to="/">前往首页</RouterLink>
    </section>

    <template v-else>
      <div class="mine-actions">
        <span>共 {{ recordings.length }} 条录音</span>
        <button type="button" @click="switchUsername">切换用户</button>
      </div>

      <p v-if="loading" class="status">正在加载...</p>
      <p v-else-if="error" class="status error">{{ error }}</p>
      <section v-else-if="!recordings.length" class="empty-card">
        <p>这个用户名还没有录音。</p>
        <RouterLink class="primary-link" to="/">去录一段</RouterLink>
      </section>

      <section v-else class="recording-list">
        <article v-for="recording in recordings" :key="recording.filename" class="recording-card">
          <div class="recording-meta">
            <time :datetime="recording.created_at">{{ formatDate(recording.created_at) }}</time>
            <strong>已被聆听 {{ recording.play_count }} 次</strong>
          </div>
          <audio controls :src="recording.url"></audio>
          <RouterLink class="public-link" :to="`/play/${recording.filename}`">
            打开公开播放页
          </RouterLink>
        </article>
      </section>

      <p v-if="recordings.length" class="preview-note">这里的录音预览不会增加播放次数。</p>
    </template>
  </main>
</template>

<style scoped>
.mine {
  width: min(720px, calc(100% - 32px));
  margin: 0 auto;
  padding: 40px 0 64px;
}

.mine-header {
  margin-bottom: 24px;
  text-align: center;
}

.mine-header h1 {
  margin: 12px 0 4px;
  font-family: var(--font-display);
  font-size: 32px;
  color: var(--neutral-700);
}

.mine-header p,
.status,
.preview-note {
  color: var(--neutral-500);
}

.back-link,
.public-link {
  color: var(--primary-600);
  text-decoration: none;
}

.mine-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--neutral-600);
}

.mine-actions button {
  border: 0;
  background: transparent;
  color: var(--primary-600);
}

.recording-list {
  display: grid;
  gap: 16px;
}

.recording-card,
.empty-card {
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--primary-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.recording-card audio {
  width: 100%;
  margin: 16px 0 10px;
}

.recording-meta {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-size: 13px;
  color: var(--neutral-500);
}

.recording-meta strong {
  color: var(--primary-600);
}

.empty-card {
  text-align: center;
}

.primary-link {
  display: inline-block;
  margin-top: 14px;
  padding: 8px 16px;
  border-radius: var(--radius-full);
  background: var(--primary-500);
  color: white;
  text-decoration: none;
}

.status,
.preview-note {
  margin-top: 16px;
  text-align: center;
}

.error {
  color: var(--accent-red);
}

@media (max-width: 480px) {
  .recording-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
