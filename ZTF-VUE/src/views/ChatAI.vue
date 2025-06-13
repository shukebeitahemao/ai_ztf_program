<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />
    <div class="flex flex-1 pt-[60px]">
      <Sidebar />
      <main class="flex-1 flex flex-col bg-paper">
        <ChatHeader />
        <ChatContainer :messages="messages" />
        <div class="mt-auto pb-6 px-6">
          <ChatInput @send-message="handleSendMessage" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import WebHeader from '../components/WebHeader.vue'
import Sidebar from '../components/Sidebar.vue'
import ChatHeader from '../components/ChatHeader.vue'
import ChatContainer from '../components/ChatContainer.vue'
import ChatInput from '../components/ChatInput.vue'

interface Message {
  id: number
  content: string
  isUser: boolean
  timestamp: Date
}

const messages = ref<Message[]>([])

const handleSendMessage = (content: string) => {
  // 添加用户消息
  const userMessage: Message = {
    id: Date.now(),
    content,
    isUser: true,
    timestamp: new Date()
  }
  messages.value.push(userMessage)

  // 添加系统自动回复
  setTimeout(() => {
    const systemMessage: Message = {
      id: Date.now(),
      content: '收到',
      isUser: false,
      timestamp: new Date()
    }
    messages.value.push(systemMessage)
  }, 500)
}
</script>
