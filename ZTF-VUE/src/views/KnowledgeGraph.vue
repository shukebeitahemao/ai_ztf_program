<template>
  <div class="flex flex-col h-screen">
    <WebHeader />
    <div class="flex-1 overflow-hidden">
      <iframe
        src="/vue_project/chat_interface_interactive.html"
        class="w-full h-full border-none"
        style="transform: scale(1); transform-origin: 0 0;"
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import WebHeader from '@/components/WebHeader.vue'
</script>

<style scoped>
iframe {
  width: 100%;
  height: 100%;
  border: none;
  overflow: hidden;
}
</style>
