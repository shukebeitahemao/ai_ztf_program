<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />
    <div class="flex-1 pt-[60px]">
      <!-- 首页内容区域 -->
      <div class="container mx-auto px-6 py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-primary mb-8">欢迎来到邹韬奋数字人文平台</h1>
          <div class="mb-8 text-gray-600">
            <p>您的用户ID:<span class="font-mono bg-gray-100 px-2 py-1 rounded">{{ userId }}</span></p>
          </div>
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
import { ref, onMounted } from 'vue'
import WebHeader from '../components/WebHeader.vue'
import { getUserId } from '../api/ftbAPI'

const userId = ref('')

// 获取用户ID
onMounted(async () => {
  try {
    userId.value = await getUserId()
  } catch (error) {
    console.error('获取用户ID失败:', error)
  }
})
</script>
