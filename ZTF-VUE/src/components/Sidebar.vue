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
            class="p-3 hover:bg-gray-100 cursor-pointer transition-colors border-b border-gray-100 group relative"
            @click="$emit('select-chat', record.id)"
          >
            <div class="flex items-start gap-2">
              <button
                class="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 text-sm px-2 py-1 bg-gray-100 rounded"
                @click.stop="handleDelete(record)"
              >
                删除
              </button>
              <div class="flex-1">
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
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { deleteSession } from '../api/ftbAPI'

// 定义组件名称
defineOptions({
  name: 'ChatSidebar'
})

interface ChatRecord {
  id: string
  title: string
  timestamp: Date
  userid: string
  topic?: string
}

//直接使用defineProps而不赋值给变量
defineProps<{
  chatRecords: ChatRecord[]
}>()

const emit = defineEmits<{
  (e: 'new-chat'): void
  (e: 'select-chat', id: string): void
  (e: 'delete-chat', id: string): void
}>()

// 处理删除
const handleDelete = async (record: ChatRecord) => {
  try {
    //正式环境
    const userId = localStorage.getItem('ztf_user_id')
    if (!userId) {
      console.error('未找到用户ID')
      return
    }
    console.log('删除会话，参数：', { userId, sessionId: record.id })
    await deleteSession(userId, record.id)
    console.log('删除会话成功')
    emit('delete-chat', record.id)
  } catch (error) {
    console.error('删除会话失败:', error)
  }
}

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
