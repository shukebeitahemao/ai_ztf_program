<template>
  <div class="w-full flex justify-end">
    <div class="relative w-[100%]">
      <textarea
        v-model="input"
        rows="3"
        class="w-full border border-gray-200 rounded-2xl p-4 pr-20 resize-none focus:outline-none focus:border-primary text-base bg-white"
        placeholder="输入您想与邹韬奋交流的内容..."
        @keydown.enter.prevent="handleSend"
      ></textarea>
      <div class="absolute bottom-4 right-4 flex flex-col items-end space-y-2">
        <button
          class="px-4 h-8 flex items-center justify-center rounded-full bg-primary hover:bg-secondary shadow transition-colors text-white text-sm"
          @click="handleSend"
        >
          发送
        </button>
        <button
          class="px-4 h-8 flex items-center justify-center rounded-full bg-gray-500 hover:bg-gray-600 shadow transition-colors text-white text-sm"
          @click="$emit('clear-messages')"
        >
          清屏
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getUserId, getCurrentSessionId, sendMessage, createNewSession } from '@/api/ftbAPI'

const input = ref('')

const emit = defineEmits(['send-message', 'system-response', 'clear-messages'])

const handleSend = async () => {
  if (input.value.trim()) {
    // const response = await fetch('http://localhost:8000/chat', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({
    //     user_msg: input.value,
    //     story_type:'',
    //     session_id:'fwergfre'
    //   })
    // })    
    // const data = await response.json()
//     const data = {
//       {
// msg:\[
// {'最后聊天时间':'2020-01-01 12:00:00'
// '主题概述':'询问邹韬奋的生平',
// 'session_id'：'sdwefasfwsefew',
// }，

// {'最后聊天时间':'2020-01-01 12:00:00'
// '主题概述':'询问邹韬奋的生平',
// 'session_id'：'sdwefasfwsefew',
// }

// \]
// }
//     }
    try {
      const user_id_get = await getUserId()
      let session_id_get = await getCurrentSessionId()
      
      // 如果没有session_id，先创建新会话
      if (!session_id_get) {
        const sessionData = await createNewSession(user_id_get)
        session_id_get = sessionData.session_id
      }
      
      // 发送用户消息
      const userMessage = input.value
      emit('send-message', userMessage)
      
      // 获取系统回复
      const data = await sendMessage(
        userMessage,
        session_id_get!,  // 使用非空断言，因为上面已经确保有值
        user_id_get,
        'test'
      )
      
      console.log('收到后端响应:', data)
      
      // 发送系统回复给父组件
      emit('system-response', data.system_msg)
      
      input.value = ''
    } catch (error) {
      console.error('发送消息失败:', error)
      // 可以添加错误提示
    }
  }
}
</script>

<style scoped>
textarea::-webkit-input-placeholder {
  color: #bdbdbd;
}
textarea:-moz-placeholder {
  color: #bdbdbd;
}
textarea::-moz-placeholder {
  color: #bdbdbd;
}
textarea:-ms-input-placeholder {
  color: #bdbdbd;
}
textarea::placeholder {
  color: #bdbdbd;
}
</style>
