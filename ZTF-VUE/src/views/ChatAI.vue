<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />  <!--顶部导航栏-->
    <div class="flex flex-1 pt-[60px]">
      <!--左侧会话列表-->
      <Sidebar
        :chat-records="chatRecords"
        @new-chat="handleNewChat()"
      />
      <main class="flex-1 flex flex-col bg-paper">
        <ChatHeader @new-chat="handleTopicChat" />  <!--顶部标题栏-->
        <ChatContainer :messages="messages" />  <!--消息列表-->
        <div class="mt-auto pb-6 px-6">
          <ChatInput @send-message="handleSendMessage" @clear-messages="handleClearMessages" /> <!--底部输入框-->
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
import { getUserId, createNewSession, getCurrentSessionId, sendMessage } from '../api/ftbAPI'

//消息结构
interface Message {
  id: number        // 消息ID
  session_id: string   //会话ID
  content: string  //内容
  timestamp: Date //时间戳
  user_id: string  // 用户ID
  isUser: boolean  // 是否是用户消息
  topic?: string  //话题
}

interface ChatRecord {  //聊天记录结构
  id: string
  title: string
  timestamp: Date
  user_id: string
  topic?: string
}

const messages = ref<Message[]>([])
const chatRecords = ref<ChatRecord[]>([])
const userId = ref('')
const currentSessionId = ref('')

// 初始化：获取用户ID和会话ID
//如果用户ID不存在，则向后端获取新用户ID
//如果会话ID不存在，则向后端获取新会话ID
//如果用户ID存在，则使用现有用户ID
//如果会话ID存在，则使用现有会话ID
onMounted(async () => {
  try {
    // 1.获取用户ID
    userId.value = await getUserId()
    console.log('userId:', userId.value)

    // 2.获取或创建会话ID
    const sessionId = getCurrentSessionId()
    if (!sessionId) {
      // 如果没有会话ID，创建新会话
      const response = await createNewSession(userId.value)
      currentSessionId.value = response.session_id

      // 创建初始会话记录
      const now = new Date()
      const chatRecord: ChatRecord = {
        id: currentSessionId.value,
        title: `会话 ${currentSessionId.value.slice(-8)}`,
        timestamp: now,
        user_id: userId.value
      }
      chatRecords.value.unshift(chatRecord)
    } else {
      // 如果有现有会话ID，使用它
      currentSessionId.value = sessionId

      // 创建现有会话的记录
      const now = new Date()
      const chatRecord: ChatRecord = {
        id: currentSessionId.value,
        title: `会话 ${currentSessionId.value.slice(-8)}`,
        timestamp: now,
        user_id: userId.value
      }
      chatRecords.value.unshift(chatRecord)
    }
    console.log('sessionId:', currentSessionId.value)
    console.log('当前会话记录数:', chatRecords.value.length)
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

// 新建聊天（无topic）
const handleNewChat = async () => {
  try {
    console.log('开始创建新会话')
    // 清空当前聊天消息
    messages.value = []

    // 创建新的会话
    const response = await createNewSession(userId.value)
    currentSessionId.value = response.session_id

    // 创建新的聊天记录
    const now = new Date()
    const chatRecord: ChatRecord = {
      id: currentSessionId.value,
      title: `会话 ${currentSessionId.value.slice(-8)}`,
      timestamp: now,
      user_id: userId.value
    }
    // 添加到聊天记录列表的开头
    chatRecords.value.unshift(chatRecord)
    console.log('新会话创建成功, sessionId:', currentSessionId.value)
    console.log('当前会话记录数:', chatRecords.value.length)
  } catch (error) {
    console.error('创建新会话失败:', error)
  }
}
// 新建带话题的聊天
const handleTopicChat = async (topic: string) => {
  try {
    console.log('开始创建话题会话:', topic)
    // 清空当前聊天消息
    messages.value = []

    // 创建新的会话
    const response = await createNewSession(userId.value)
    currentSessionId.value = response.session_id

    // 创建新的聊天记录
    const now = new Date()
    const chatRecord: ChatRecord = {
      id: currentSessionId.value,
      title: `${topic} - ${currentSessionId.value.slice(-8)}`,
      timestamp: now,
      user_id: userId.value,
      topic: topic
    }

    // 添加到聊天记录列表的开头
    chatRecords.value.unshift(chatRecord)
    console.log('新话题会话创建成功, sessionId:', currentSessionId.value, 'topic:', topic)
    console.log('当前会话记录数:', chatRecords.value.length)
  } catch (error) {
    console.error('创建话题会话失败:', error)
  }
}

// 清空消息
const handleClearMessages = () => {
  messages.value = []
}

// 发送消息
const handleSendMessage = async (content: string) => {
  const now = new Date()

  // 添加用户消息到界面
  const userMessage: Message = {
    id: Date.now(),
    session_id: currentSessionId.value,
    content,
    isUser: true,
    timestamp: now,
    user_id: userId.value
  }
  messages.value.push(userMessage)

  // 发送消息到服务器
  try {
    // 获取当前会话的话题（如果有的话）
    const currentChat = chatRecords.value.find(record => record.id === currentSessionId.value)
    const story_type = currentChat?.topic || ''

    // 发送消息到后端
    const response = await sendMessage(
      content,  // user_msg
      currentSessionId.value,  // session_id
      userId.value,  // user_id
      story_type  // story_type
    )

    // 添加系统回复
    const systemMessage: Message = {
      id: Date.now() + 1,
      session_id: response.sessionid,
      content: response.system_msg,
      isUser: false,
      timestamp: new Date(),
      user_id: 'system'
    }
    messages.value.push(systemMessage)
  } catch (error) {
    console.error('发送消息失败:', error)
    // 添加错误提示消息
    const errorMessage: Message = {
      id: Date.now() + 1,
      session_id: currentSessionId.value,
      content: '消息发送失败，请稍后重试',
      isUser: false,
      timestamp: new Date(),
      user_id: 'system'
    }
    messages.value.push(errorMessage)
  }
}
</script>
