<template>
  <aside class="w-64 bg-white border-r border-gray-200">
    <div class="h-full flex flex-col">
      <div class="p-4 border-b border-gray-200">
        <button
          @click="$emit('new-chat')"
          class="w-full py-2 px-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
        >
          新建会话
        </button>
      </div>
      <div class="flex-1 overflow-y-auto">
        <div v-if="chatRecords.length === 0" class="p-4 text-gray-500 text-center">
          暂无会话记录
        </div>
        <div v-else class="space-y-1">
          <div
            v-for="record in chatRecords"
            :key="record.id"
            class="p-3 hover:bg-gray-100 cursor-pointer transition-colors border-b border-gray-100"
            @click="$emit('select-chat', record.id)"
          >
            <div class="text-sm font-medium truncate">
              {{ record.title }}
              <span v-if="record.topic" class="ml-1 text-xs text-primary">[{{ record.topic }}]</span>
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ formatTime(record.timestamp) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
// 定义组件名称
defineOptions({
  name: 'ChatSidebar'
})

interface ChatRecord {
  id: string
  title: string
  timestamp: Date
  user_id: string
  topic?: string
}

defineProps<{
  chatRecords: ChatRecord[]
}>()

defineEmits<{
  (e: 'new-chat'): void
  (e: 'select-chat', id: string): void
}>()

// 格式化时间
const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>
