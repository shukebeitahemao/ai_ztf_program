<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />
    <div class="flex flex-1 pt-[60px]">
      <!--侧边栏，不带topic的新建对话-->
      <Sidebar
        :chat-records="chatRecords"
        @new-chat="handleNewChat()"
      />
      <main class="flex-1 flex flex-col bg-paper">
        <ChatHeader @new-chat="handleNewChat" />
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
import { createNewChat, sendMessage } from '../api/ftbAPI'

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
  topic?: string
}

const messages = ref<Message[]>([])
const chatRecords = ref<ChatRecord[]>([])
const userUID = ref('')
const isFirstMessage = ref(true)
const currentChatId = ref('')

onMounted(async () => {
  userUID.value = await getOrCreateUID()
})
// 格式化聊天标题
const formatChatTitle = (uid: string, date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${uid}_${year}${month}${day}_${hours}${minutes}`
}
// 新建聊天
const handleNewChat = async (topic: string = '') => {
  // 清空当前聊天消息
  messages.value = []
  // 重置首次消息标志
  isFirstMessage.value = true

  // 创建新的聊天记录
  const now = new Date()
  const chatRecord: ChatRecord = {
    id: formatChatTitle(userUID.value, now),
    title: formatChatTitle(userUID.value, now),
    timestamp: now,
    uid: userUID.value,
    topic
  }

  // 添加到聊天记录列表
  chatRecords.value.push(chatRecord)
  // 更新当前聊天ID
  currentChatId.value = chatRecord.id

  // 发送到后端
  try {
    await createNewChat(chatRecord.id, topic)
    if (topic) {
      console.log('Creating new chat with topic:', topic)
    } else {
      console.log('Creating new chat without topic')
    }
  } catch (error) {
    console.error('创建聊天记录失败:', error)
  }
}
// 发送消息
const handleSendMessage = async (content: string) => {
  const now = new Date()

  // 添加用户消息
  const userMessage: Message = {
    id: Date.now(),
    content,
    isUser: true,
    timestamp: now,
    uid: userUID.value
  }
  messages.value.push(userMessage)

  // 发送消息到服务器
  try {
    const response = await sendMessage(content, currentChatId.value, userUID.value, now)
    // 添加系统回复
    const systemMessage: Message = {
      id: Date.now(),
      content: response.reply || '后端已收到您的消息',
      isUser: false,
      timestamp: new Date(),
      uid: 'system'
    }
    messages.value.push(systemMessage)
  } catch (error) {
    console.error('发送消息失败:', error)
    // 添加错误提示消息
    const errorMessage: Message = {
      id: Date.now(),
      content: '消息发送失败，请稍后重试',
      isUser: false,
      timestamp: new Date(),
      uid: 'system'
    }
    messages.value.push(errorMessage)
  }
}
</script>
