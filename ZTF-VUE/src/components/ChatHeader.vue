<template>
  <div class="p-6 border-b border-gray-200">
    <h1 class="text-2xl font-bold text-ink">与邹韬奋聊一聊</h1>

    <div class="mt-4 flex space-x-3 overflow-x-auto pb-2">
      <button v-for="topic in topics"
              :key="topic"
              class="flex-shrink-0 bg-white hover:bg-gray-50 border border-gray-200 px-4 py-2 rounded-xl whitespace-nowrap transition-colors"
              @click="selectTopic(topic)">
        {{ topic }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const topics = ref([
  '七君子事件',
  '《生活》周刊',
  '生活书店',
  '职业选择',
  '少年时代',
  '英语学习'
])

const selectTopic = (topic: string) => {
  // 实现选择话题的逻辑
}
</script>