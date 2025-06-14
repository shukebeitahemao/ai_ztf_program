<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />
    <div class="flex flex-1 pt-[60px]">
      <Sidebar
        :chat-records="chatRecords"
        @new-chat="handleNewChat"
      />
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
import { ref, onMounted } from 'vue'
import WebHeader from '../components/WebHeader.vue'
import Sidebar from '../components/Sidebar.vue'
import ChatHeader from '../components/ChatHeader.vue'
import ChatContainer from '../components/ChatContainer.vue'
import ChatInput from '../components/ChatInput.vue'
import { getOrCreateUID } from '../utils/user'

interface Message {
  id: number
  content: string
  isUser: boolean
  timestamp: Date
  uid: string
}

interface ChatRecord {
  id: string
  title: string
  timestamp: Date
  uid: string
}

const messages = ref<Message[]>([])
const chatRecords = ref<ChatRecord[]>([])
const userUID = ref('')
const isFirstMessage = ref(true)

onMounted(() => {
  userUID.value = getOrCreateUID()
})

const formatChatTitle = (uid: string, date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${uid}_${year}${month}${day}_${hours}${minutes}`
}

const handleNewChat = () => {
  // 清空当前聊天消息
  messages.value = []
  // 重置首次消息标志
  isFirstMessage.value = true
}

const handleSendMessage = (content: string) => {
  // 添加用户消息
  const userMessage: Message = {
    id: Date.now(),
    content,
    isUser: true,
    timestamp: new Date(),
    uid: userUID.value
  }
  messages.value.push(userMessage)

  // 如果是第一条消息，创建聊天记录
  if (isFirstMessage.value) {
    const now = new Date()
    const chatRecord: ChatRecord = {
      id: formatChatTitle(userUID.value, now),
      title: formatChatTitle(userUID.value, now),
      timestamp: now,
      uid: userUID.value
    }
    chatRecords.value.push(chatRecord)
    isFirstMessage.value = false
  }

  // 添加系统自动回复
  setTimeout(() => {
    const systemMessage: Message = {
      id: Date.now(),
      content: '收到',
      isUser: false,
      timestamp: new Date(),
      uid: 'system'
    }
    messages.value.push(systemMessage)
  }, 500)
}
</script>
