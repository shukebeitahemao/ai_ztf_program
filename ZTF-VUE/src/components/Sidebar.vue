<template>
  <aside class="w-64 bg-white border-r border-gray-200 h-full">
    <div class="p-4">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-800">聊天记录</h2>
        <button
          @click="handleNewChat"
          class="text-primary hover:text-secondary transition-colors"
          title="新建对话"
        >
          <i class="fas fa-plus"></i>
        </button>
      </div>
      <div v-if="chatRecords.length === 0" class="text-gray-500 text-sm">
        暂无聊天记录
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="record in chatRecords"
          :key="record.id"
          class="p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="text-sm font-medium text-gray-800">{{ record.title }}</div>
          <div class="text-xs text-gray-500 mt-1">
            {{ formatTime(record.timestamp) }}
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { getOrCreateUID } from '../utils/user'

interface ChatRecord {
  id: string
  title: string
  timestamp: Date
  uid: string
}

const props = defineProps<{
  chatRecords: ChatRecord[]
}>()

const emit = defineEmits<{
  (e: 'new-chat'): void
}>()

const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const handleNewChat = () => {
  emit('new-chat')
}
</script>