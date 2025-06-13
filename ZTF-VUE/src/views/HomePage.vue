<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />
    <div class="flex-1 pt-[60px]">
      <!-- 首页内容区域 -->
      <div class="container mx-auto px-6 py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-primary mb-8">欢迎来到邹韬奋数字人文平台</h1>
          <router-link
            to="/chat"
            class="inline-block px-8 py-4 bg-primary text-white rounded-full hover:bg-secondary transition-colors"
          >
            对话邹韬奋
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import WebHeader from '../components/WebHeader.vue'
</script>
