<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />  <!--顶部导航栏-->
    <div class="flex flex-1 pt-[60px]">
      <!--左侧会话列表-->
      <Sidebar
        :chat-records="chatRecords"
        @new-chat="handleNewChat()"
        @select-chat="handleSelectChat"
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
import { getUserId, createNewSession, sendMessage, loadSpecificSession, loadHistory } from '../api/ftbAPI'

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
onMounted(async () => {
  try {
    // 1.获取用户ID
    const storedUserId = localStorage.getItem('ztf_user_id')

    if (storedUserId) {
      // 如果本地存在用户ID，加载历史记录
      userId.value = storedUserId
      console.log('已存在的用户ID:', userId.value)

      // 加载历史记录
      const historyResponse = await loadHistory(userId.value)

      // 按更新时间降序排序
      const sortedHistory = historyResponse.msg.sort((a, b) =>
        new Date(b.update_time).getTime() - new Date(a.update_time).getTime()
      )

      // 转换为ChatRecord格式并更新列表
      chatRecords.value = sortedHistory.map(session => ({
        id: session.session_id,
        title: session.abstract,
        timestamp: new Date(session.update_time),
        user_id: userId.value
      }))

      // 创建新会话
      await handleNewChat()

    } else {
      // 如果本地没有用户ID，直接创建新会话
      userId.value = await getUserId()
      console.log('新创建的用户ID:', userId.value)
      await handleNewChat()
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

// 处理选择特定会话
const handleSelectChat = async (sessionId: string) => {
  try {
    console.log('选择会话:', sessionId)
    // 清空当前消息列表
    messages.value = []

    // 更新当前会话ID
    currentSessionId.value = sessionId

    // 加载会话历史记录
    const response = await loadSpecificSession(userId.value, sessionId)

    // 解析历史记录
    const history = JSON.parse(response.msg[0].history)

    // 将历史记录转换为消息格式并添加到消息列表
    history.forEach((item: { role: string; content: string }, index: number) => {
      const message: Message = {
        id: Date.now() + index,
        session_id: sessionId,
        content: item.content,
        isUser: item.role === 'user',
        timestamp: new Date(),
        user_id: item.role === 'user' ? userId.value : 'system'
      }
      messages.value.push(message)
    })

    console.log('历史记录加载成功')
  } catch (error) {
    console.error('加载会话历史记录失败:', error)
  }
}
</script>
