<template>
  <div class="flex flex-col h-screen w-full">
    <WebHeader />
    <div class="flex-1 overflow-hidden w-full mt-[10px]">
      <iframe
        src="/vue_project/kg_echarts_solution.html"
        class="w-full h-full border-none"
        style="transform: scale(1); transform-origin: 0 0; margin-top: 0-200px; width: 100vw; height: calc(100vh);"
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import WebHeader from '@/components/WebHeader.vue'
</script>

<style scoped>
.h-screen {
  height: 100vh;
}

.w-full {
  width: 100%;
}

.flex-1 {
  flex: 1 1 0%;
}

.overflow-hidden {
  overflow: hidden;
}

iframe {
  width: 100vw;
  height: calc(100vh - 64px);
  border: none;
  overflow: hidden;
  display: block;
}
</style>
