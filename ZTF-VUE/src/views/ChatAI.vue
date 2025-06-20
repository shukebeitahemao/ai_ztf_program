<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />  <!--顶部导航栏-->
    <div class="flex flex-1 pt-[60px]">
      <!--左侧会话列表-->
      <Sidebar
        :chat-records="chatRecords"
        @new-chat="handleNewChat()"
        @select-chat="handleSelectChat"
        @delete-chat="handleDeleteChat"
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
import { getUserId, createNewSession, sendMessage, loadSpecificSession, loadHistory, deleteSession, saveUserMsg } from '../api/ftbAPI'

//消息结构
interface Message {
  id: number        // 消息ID
  sessionid: string   //会话ID
  content: string  //内容
  timestamp: Date //时间戳
  userid: string  // 用户ID
  isUser: boolean  // 是否是用户消息
  topic?: string  //话题
}

interface ChatRecord {  //聊天记录结构
  id: string
  title: string
  timestamp: Date
  userid: string
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
      console.log('钩子获取历史记录')

      // 按更新时间降序排序
      const sortedHistory = historyResponse.msg.sort((a, b) =>
        new Date(b.update_time).getTime() - new Date(a.update_time).getTime()
      )
      // 转换为ChatRecord格式并更新列表
      chatRecords.value = sortedHistory.map(session => ({
        id: session.sessionid,
        title: session.abstract,
        timestamp: new Date(session.update_time),
        userid: userId.value
      }))
      console.log('更新列表')

      // 如果没有历史会话，创建新会话
      if (chatRecords.value.length === 0) {
        await handleNewChat()
        console.log('无历史会话，创建新会话')
      } else {
        // 使用最新的会话作为当前会话
        currentSessionId.value = chatRecords.value[0].id
        console.log('使用最新会话:', currentSessionId.value)
      }
    } else {
      // 如果本地没有用户ID，先获取userid再创建新会话
      userId.value = await getUserId()
      console.log('新创建的用户ID:', userId.value)
      await handleNewChat()
      console.log('创建新会话', currentSessionId.value)
    }

    // 添加页面关闭时的自动保存功能
    window.addEventListener('beforeunload', async () => {
      try {
        if (userId.value) {
          await saveUserMsg(userId.value)
        }
      } catch (error) {
        console.error('自动保存失败:', error)
      }
    })
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

// 新建聊天（无topic）
const handleNewChat = async () => {
  try {
    // 如果当前有会话且有消息，才保存
    if (currentSessionId.value && messages.value.length > 0) {
      await saveUserMsg(userId.value)
      console.log('保存当前会话')
    }
    console.log('有会话内容，保存会话；没有就不保存')
    // 清空当前聊天消息
    messages.value = []
    console.log('清空当前聊天消息')
    // 创建新的会话
    const response = await createNewSession(userId.value)
    currentSessionId.value = response.sessionid
    console.log('创建新会话')

    // 创建新会话后再加载历史记录
    const historyResponse = await loadHistory(userId.value)
    console.log('获取历史会话')
    // 按更新时间降序排序
    const sortedHistory = historyResponse.msg.sort((a, b) =>
      new Date(b.update_time).getTime() - new Date(a.update_time).getTime()
    )
    // 转换为ChatRecord格式并更新列表
    chatRecords.value = sortedHistory.map(session => ({
      id: session.sessionid,
      title: session.abstract,
      timestamp: new Date(session.update_time),
      userid: userId.value
    }))
  }catch (error) {
    console.error('创建新会话失败:', error)
  }
}
// 新建带话题的聊天
const handleTopicChat = async (topic: string) => {
  try {
    // 如果当前有会话且有消息，才保存
    if (currentSessionId.value && messages.value.length > 0) {
      await saveUserMsg(userId.value)
      console.log('保存当前会话')
    }
    console.log('有会话内容，保存会话；没有就不保存')

    // 清空当前聊天消息
    messages.value = []
    console.log('清空当前聊天消息')

    // 创建新的会话
    const response = await createNewSession(userId.value)
    currentSessionId.value = response.sessionid

    // 将topic存储到localStorage
    localStorage.setItem(`topic_${response.sessionid}`, topic)
    console.log('创建新会话，ID:', currentSessionId.value, '话题:', topic)

    // 创建新会话后再加载历史记录
    const historyResponse = await loadHistory(userId.value)
    console.log('获取历史会话')

    // 按更新时间降序排序
    const sortedHistory = historyResponse.msg.sort((a, b) =>
      new Date(b.update_time).getTime() - new Date(a.update_time).getTime()
    )

    // 转换为ChatRecord格式并更新列表，使用后端返回的abstract
    chatRecords.value = sortedHistory.map(session => ({
      id: session.sessionid,
      title: session.abstract,  // 直接使用后端返回的abstract
      timestamp: new Date(session.update_time),
      userid: userId.value,
      topic: localStorage.getItem(`topic_${session.sessionid}`) || ''  // 从localStorage获取topic
    }))
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
    sessionid: currentSessionId.value,
    content,
    isUser: true,
    timestamp: now,
    userid: userId.value
  }
  messages.value.push(userMessage)

  // 发送消息到服务器
  try {
    // 从localStorage获取当前会话的topic
    const story_type = localStorage.getItem(`topic_${currentSessionId.value}`) || ''

    // 发送消息到后端
    const response = await sendMessage(
      content,  // user_msg
      currentSessionId.value,  // sessionid
      userId.value,  // userid
      story_type  // story_type
    )

    // 添加系统回复
    const systemMessage: Message = {
      id: Date.now() + 1,
      sessionid: response.sessionid,
      content: response.system_msg,
      isUser: false,
      timestamp: new Date(),
      userid: 'system'
    }
    messages.value.push(systemMessage)
  } catch (error) {
    console.error('发送消息失败:', error)
    // 添加错误提示消息
    const errorMessage: Message = {
      id: Date.now() + 1,
      sessionid: currentSessionId.value,
      content: '消息发送失败，请稍后重试',
      isUser: false,
      timestamp: new Date(),
      userid: 'system'
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
        sessionid: sessionId,
        content: item.content,
        isUser: item.role === 'user',
        timestamp: new Date(),
        userid: item.role === 'user' ? userId.value : 'system'
      }
      messages.value.push(message)
    })

    console.log('历史记录加载成功')
  } catch (error) {
    console.error('加载会话历史记录失败:', error)
  }
}

// 处理删除会话
const handleDeleteChat = async (sessionId: string) => {
  try {
    /* 正式环境
    const userId = localStorage.getItem('ztf_user_id')
    if (!userId) {
      console.error('未找到用户ID')
      return
    }
    */

    // 测试环境
    const userId = '123' // 使用测试用户ID
    // 调用删除API
    await deleteSession(userId, sessionId)
    // 从会话记录中移除
    chatRecords.value = chatRecords.value.filter(record => record.id !== sessionId)
    // 如果删除的是当前会话，创建新会话
    if (currentSessionId.value === sessionId) {
      handleNewChat()
    }
    console.log('会话删除成功:', sessionId)
  } catch (error) {
    console.error('删除会话失败:', error)
  }
}
</script>
