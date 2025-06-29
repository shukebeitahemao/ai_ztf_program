<template>
  <div class="min-h-screen flex flex-col">
    <WebHeader />  <!--顶部导航栏-->
    <div class="flex flex-1 pt-[60px]">
      <!--左侧会话列表-->
      <Sidebar
        :chat-records="chatRecords"
        @new-chat="handleNewChat"
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
import { ref, onMounted ,onUnmounted} from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import WebHeader from '../components/WebHeader.vue'
import Sidebar from '../components/Sidebar.vue'
import ChatHeader from '../components/ChatHeader.vue'
import ChatContainer from '../components/ChatContainer.vue'
import ChatInput from '../components/ChatInput.vue'
//修改
//import { getUserId, createNewSession, sendMessage, loadSpecificSession, loadHistory, deleteSession, saveUserMsg, saveUserMsgOnUnload } from '../api/ftbAPI'
import { getUserId, createNewSession, sendMessage, loadSpecificSession, loadHistory, deleteSession, saveUserMsg, saveUserMsgOnUnload } from '../api/ftbAPI'
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

// 清理事件监听器
// onUnmounted(() => {
//   window.removeEventListener('beforeunload', handlePageUnload)
//   window.removeEventListener('pagehide', handlePageUnload)
//   document.removeEventListener('visibilitychange', handleVisibilityChange)
// })

//修改
// 添加防重复调用的标志
// let isSaving = false


// // 普通的保存函数（用于路由切换等场景）
// const handleSaveUserMsg = async () => {
//   if (isSaving || !userId.value || messages.value.length === 0) return
  
//   isSaving = true
//   try {
//     await saveUserMsg(userId.value)
//     localStorage.setItem('ztf_session_id', currentSessionId.value)
//     console.log('保存成功')
//   } catch (error) {
//     console.error('保存失败:', error)
//   } finally {
//     isSaving = false
//   }
// }

// // 页面卸载时的保存函数（使用sendBeacon）
// const handlePageUnload = () => {
//   if (!userId.value || isSaving || messages.value.length === 0) return
  
//   // 使用 sendBeacon 确保请求不被中止
//   const success = saveUserMsgOnUnload(userId.value)
//   console.log('页面卸载保存:', success ? '成功' : '失败')
  
//   // 保存会话ID到localStorage
//   if (currentSessionId.value) {
//     localStorage.setItem('ztf_session_id', currentSessionId.value)
//   }
// }

// // 页面可见性变化时的保存（更可靠的保存时机）
// const handleVisibilityChange = () => {
//   // 当页面变为隐藏状态时保存
//   if (document.hidden && userId.value && !isSaving && messages.value.length > 0) {
//     handleSaveUserMsg()
//   }
// }

// 路由离开前保存
onBeforeRouteLeave((to, from) => {
  if (userId.value && messages.value.length > 0) {
    try {
      //修改
      saveUserMsg(userId.value)
      // handleSaveUserMsg()
      localStorage.setItem('ztf_session_id', currentSessionId.value)
      console.log('跳转前保存成功')
    } catch (error) {
      console.error('跳转保存失败:', error)
    }
  }
})

// 初始化：获取用户ID和会话ID
onMounted(async () => {
  try {
    // 1.获取用户ID
    userId.value = await getUserId()
    console.log('1-获取到的用户ID:', userId.value)

    // 2.加载历史记录
    const sortedHistory = await loadHistoryRecords()
    console.log('1-加载历史记录',sortedHistory)
    // 3.如果历史记录为空，创建新会话
    if (!sortedHistory) {
      console.log('**历史记录为空，开始创建新会话')
      await handleNewChat()
      return
    }

    // 4.获取最近的会话ID
    const lastSessionId = sortedHistory[0]?.session_id
    if (lastSessionId) {
      currentSessionId.value = lastSessionId
      // 加载最近的会话内容
      await handleSelectChat(lastSessionId)
      console.log('1-加载最近的会话')
    } else {
      // 如果没有会话ID，创建新会话
      await handleNewChat()
      console.log('1-没有可用的会话ID，创建新会话')
    }
  } catch (error) {
    console.error('1-初始化失败:', error)
    // 如果发生错误，创建新会话
    await handleNewChat()
    console.log('1-初始化失败，创建新会话')
  }
  //修改
  //  // 监听页面卸载事件（使用sendBeacon）
  //  window.addEventListener('beforeunload', handlePageUnload)
  // window.addEventListener('pagehide', handlePageUnload) // 移动端兼容
  
  // 监听页面可见性变化（更可靠的保存时机）
  // document.addEventListener('visibilitychange', handleVisibilityChange)

  // 添加页面关闭时的自动保存功能
  window.addEventListener('beforeunload', async () => {
    try {
      if (userId.value) {
        await saveUserMsg(userId.value)
        // 保存当前会话ID
        localStorage.setItem('ztf_session_id', currentSessionId.value)
        console.log('自动保存成功')
      }
    // 暂停100秒
    // await new Promise(resolve => setTimeout(resolve, 100000))
    } catch (error) {
      console.error('自动保存失败:', error)
    }
  })
  // //添加浏览器后退时自动保存
  // window.addEventListener('popstate', async () => {
  //   try {
  //     if (userId.value) {
  //       await saveUserMsg(userId.value)
  //       // 保存当前会话ID
  //       localStorage.setItem('ztf_session_id', currentSessionId.value)
  //       console.log('自动保存成功')
  //     }
  //   } catch (error) {
  //     console.error('自动保存失败:', error)
  //   }
  // })
}
)

// 加载历史记录
const loadHistoryRecords = async () => {
  try {
    // 加载历史记录
    const historyResponse = await loadHistory(userId.value)
    console.log('加载历史记录', historyResponse)
    if (!historyResponse || !historyResponse.msg || historyResponse.msg.length === 0) {
      chatRecords.value = []
      return null
    }

    // 过滤有内容的会话，删除空会话
    const validSessions = []
    for (const session of historyResponse.msg) {
      if (String(session.session_id) === '10001' || Number(session.session_id) === 10001) {
        continue // 跳过默认会话
      }
      try {
        const response = await loadSpecificSession(userId.value, session.session_id)
        const history = JSON.parse(response.msg[0].history)
        if (history && history.length > 0) {
          validSessions.push(session) // 有内容的会话保留
        } else {
          // 删除空会话
          await deleteSession(userId.value, session.session_id)
          console.log('删除空会话:', session.session_id)
        }
      } catch (error) {
        console.error('检查会话内容失败:', session.session_id, error)
      }
    }
    // 按更新时间降序排序
    const sortedHistory = validSessions.sort((a, b) =>
      new Date(b.update_time).getTime() - new Date(a.update_time).getTime()
    )

    // 转换为ChatRecord格式并更新列表
    chatRecords.value = sortedHistory.map(session => ({
      id: session.session_id,
      title: session.abstract,
      timestamp: new Date(session.update_time),
      userid: userId.value,
      topic: localStorage.getItem(`topic_${session.session_id}`) || ''
    }))

    console.log('有效的历史记录:', sortedHistory)
    return sortedHistory
  } catch (error) {
    console.error('加载历史记录失败:', error)
    chatRecords.value = []

    return null
  }
}

// 新建聊天（无topic）
const handleNewChat = async () => {
  try {
    // 当前有会话且有消息，保存-清屏
    console.log('2-handleNewChat')
    if (currentSessionId.value && messages.value.length > 0) {
      await saveUserMsg(userId.value)
      console.log('2-保存当前会话')
      messages.value = []
      console.log('2-保存完成，清空当前聊天消息')
    }
    // 加载历史记录
    await loadHistoryRecords()
    console.log('2-获取历史会话')
    const response = await createNewSession(userId.value)
    currentSessionId.value = response.session_id
    //将sessionid存储到localStorage
    localStorage.setItem(`topic_${response.session_id}`, '')
    console.log('创建新会话，ID:', currentSessionId.value)
  } catch (error) {
    console.error('2-创建新会话失败:', error)
  }
}

// 新建带话题的聊天
const handleTopicChat = async (topic: string) => {
  try {
    //如果当前有会话且有消息，才保存-清屏
    if (currentSessionId.value && messages.value.length > 0) {
      await saveUserMsg(userId.value)
      console.log('3-保存当前会话')
      messages.value = []
      console.log('3-保存完成，清空当前聊天消息')
    }
    // 加载历史记录
    await loadHistoryRecords()
    console.log('3-获取历史会话')
    // 创建新的会话
    const response = await createNewSession(userId.value)
    currentSessionId.value = response.session_id
    // 将sessionid和topic存储到localStorage
    localStorage.setItem(`topic_${response.session_id}`, topic)
    console.log('创建新会话，ID:', currentSessionId.value, '话题:', topic)
  } catch (error) {
    console.error('3-创建话题会话失败:', error)
  }
}

// 发送消息
const handleSendMessage = async (content: string) => {
  const now = new Date()
  console.log('触发handlesendmessage函数',content)
  // 检查会话ID是否存在
  if (!currentSessionId.value) {
    console.error('会话ID不存在，创建新会话')
    await handleNewChat()
  }
  console.log('会话ID存在',currentSessionId.value)
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
    console.log('发送消息到后端',story_type)
    // 发送消息到后端
    const response = await sendMessage(
      content,  // user_msg
      currentSessionId.value,  // sessionid
      userId.value,  // userid
      story_type  // story_type
    )
    console.log('发送消息到后端',response)
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
  } catch (error: any) {
    console.error('发送消息失败:', error)
    // 添加更详细的错误提示消息
    const errorMessage: Message = {
      id: Date.now() + 1,
      sessionid: currentSessionId.value,
      content: `消息发送失败: ${error.response?.data?.detail || error.message || '请稍后重试'}`,
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
    // 保存选中的会话ID到本地存储
    localStorage.setItem('ztf_session_id', sessionId)
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
    //正式环境
    const userId = localStorage.getItem('ztf_user_id')
    if (!userId) {
      console.error('未找到用户ID')
      return
    }

    // 调用删除API
    await deleteSession(userId, sessionId)
    // 从会话记录中移除
    chatRecords.value = chatRecords.value.filter(record => record.id !== sessionId)

    // 如果删除的是当前会话
    if (currentSessionId.value === sessionId) {
      // 从本地存储中移除会话ID
      localStorage.removeItem('ztf_session_id')
      handleNewChat()
    }
    console.log('会话删除成功:', sessionId)
  } catch (error) {
    console.error('删除会话失败:', error)
  }
}

// 清空消息
const handleClearMessages = () => {
  messages.value = []
  console.log('清空当前聊天消息')
}
</script>
