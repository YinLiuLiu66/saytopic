<script setup>
// 全站底部信息：品牌行 + 工信部备案号（备案号必须链接到工信部官网，见 docs/部署文档.md）
const ICP_NUMBER = '冀ICP备2026039990号-1'
const ICP_LINK = 'https://beian.miit.gov.cn/'
</script>

<template>
  <footer class="site-footer">
    <span>SayTopic - 声音家书，传递感恩</span>
    <span class="sep">·</span>
    <a :href="ICP_LINK" target="_blank" rel="noreferrer noopener">{{ ICP_NUMBER }}</a>
  </footer>
</template>

<style scoped>
.site-footer {
  position: fixed;
  left: 50%;
  bottom: 12px;
  transform: translateX(-50%);
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.6);
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 1px;
  color: var(--neutral-400);
  white-space: nowrap;
  /* 只让链接可点，避免遮挡页面其他区域 */
  pointer-events: none;
}

.site-footer a {
  color: inherit;
  text-decoration: none;
  pointer-events: auto;
}

.site-footer a:hover {
  color: var(--primary-500);
  text-decoration: underline;
}

.sep {
  opacity: 0.7;
}

@media (max-width: 480px) {
  .site-footer {
    font-size: 11px;
    letter-spacing: 0;
  }
}
</style>
