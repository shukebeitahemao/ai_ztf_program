<template>
  <div class="border-b border-gray-200 bg-white">
    <div class="px-6 py-4">
      <div class="flex items-center space-x-4 overflow-x-auto pb-2">
        <button v-for="topic in topics"
                :key="topic"
                class="flex-shrink-0 bg-white hover:bg-gray-50 border border-gray-200 px-4 py-2 rounded-xl whitespace-nowrap transition-colors"
                @click="handleTopicClick(topic)">
          {{ topic }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const topics = [
  '邹韬奋生平',
  '生活书店',
  '七君子事件',
  '新闻思想',
  '出版事业',
  '教育理念'
]

const emit = defineEmits<{
  (e: 'new-chat', topic: string): void
}>()

const handleTopicClick = (topic: string) => {
  console.log('Selected topic:', topic)
  emit('new-chat', topic)
}
</script>