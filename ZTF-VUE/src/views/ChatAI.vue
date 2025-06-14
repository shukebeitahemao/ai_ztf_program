<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />
    <div class="flex flex-1 pt-[60px]">
      <Sidebar
        :chat-records="chatRecords"
        @new-chat="handleNewChat"
      />
      <main class="flex-1 flex flex-col bg-paper">
        <ChatHeader @new-chat="handleNewChatWithTopic" />
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
import axios from 'axios'

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
const API_BASE_URL = 'http://localhost:3000' // 根据实际后端地址修改

onMounted(async () => {
  userUID.value = await getOrCreateUID()
})
// 格式化聊天标题,是往后端传输的session_id
const formatChatTitle = (uid: string, date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${uid}_${year}${month}${day}_${hours}${minutes}`
}
// 新建聊天
const handleNewChat = () => {
  // 清空当前聊天消息
  messages.value = []
  // 重置首次消息标志
  isFirstMessage.value = true
}
// 新建聊天，带话题
const handleNewChatWithTopic = (topic: string) => {
  handleNewChat()
  // 这里可以添加与后端通信的代码
  console.log('Creating new chat with topic:', topic)
}
// 发送消息
const handleSendMessage = async (content: string) => {
  // 添加用户消息
  const userMessage: Message = {
    id: Date.now(),
    content,
    isUser: true,
    timestamp: new Date(),
    uid: userUID.value
  }
  messages.value.push(userMessage)

  // 如果是第一条消息，触发形成chatRecord记录号
  if (isFirstMessage.value) {
    const now = new Date()
    const chatRecord: ChatRecord = {
      id: formatChatTitle(userUID.value, now),
      title: formatChatTitle(userUID.value, now),
      timestamp: now,
      uid: userUID.value
    }
    chatRecords.value.push(chatRecord)
    console.log('chatRecord:', chatRecord)
    isFirstMessage.value = false

    // 发送 ChatRecord 到后端
    try {
      const response = await axios.post(`${API_BASE_URL}/chat/create_new_chat`, chatRecord)
      console.log('生成的聊天记录:', chatRecord)
      console.log('服务器响应:', response.data)
    } catch (error) {
      console.error('发送聊天记录失败:', error)
    }
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
