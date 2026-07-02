<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <RouterView />
  </div>
</template>

<style>
.app-shell {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 磁带纹理背景 */
.app-shell::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 3px,
      rgba(168, 216, 234, 0.04) 3px,
      rgba(168, 216, 234, 0.04) 4px
    );
  pointer-events: none;
  z-index: 0;
}
</style>
