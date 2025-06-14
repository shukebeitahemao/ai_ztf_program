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
      <div class="absolute bottom-4 right-4 flex items-center space-x-2">
        <!--<button class="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200">
          <i class="fas fa-microphone text-gray-500"></i>
        </button>-->
        <button
          class="w-10 h-10 flex items-center justify-center rounded-full bg-primary hover:bg-secondary shadow transition-colors"
          @click="handleSend"
        >
          <i class="fas fa-paper-plane text-white"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const input = ref('')

const emit = defineEmits(['send-message'])

const handleSend = () => {
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
// ‘session_id’：‘sdwefasfwsefew’,
// }，

// {'最后聊天时间':'2020-01-01 12:00:00'
// '主题概述':'询问邹韬奋的生平',
// ‘session_id’：‘sdwefasfwsefew’,
// }

// \]
// }
//     }
    console.log('收到后端响应:', data)
    emit('send-message', input.value)
    input.value = ''
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
