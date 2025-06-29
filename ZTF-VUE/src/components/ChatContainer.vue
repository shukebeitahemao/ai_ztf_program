<template>
  <div class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
    <div v-for="message in messages" :key="message.id" class="message-animation">
      <div class="flex items-start gap-4" :class="message.isUser ? 'flex-row-reverse' : 'flex-row'">
        <div class="w-10 h-10 flex-shrink-0">
          <img
            :src="message.isUser ? '/avatars/user-avatar.png' : '/avatars/system-avatar.png'"
            :alt="message.isUser ? '用户头像' : '系统头像'"
            class="w-full h-full rounded-full object-cover"
          />
        </div>
        <div :class="[
          'max-w-[80%] rounded-2xl p-4',
          message.isUser
            ? 'bg-primary text-white'
            : 'bg-white text-gray-800'
        ]">
          <div class="text-sm">{{ message.content }}</div>
          <div :class="[
            'text-xs mt-1',
            message.isUser ? 'text-white/70' : 'text-gray-500'
          ]">
            {{ formatTime(message.timestamp) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Message {
  id: number
  content: string
  isUser: boolean
  timestamp: Date
}

defineProps<{
  messages: Message[]
}>()

const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>

<style scoped>
.message-animation {
  animation: messageFadeIn 0.3s ease-out;
}

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
