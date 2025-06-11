<template>
  <div class="flex-1 overflow-y-auto chat-container p-6 space-y-6">
    <div v-for="(message, index) in messages" :key="index" 
         :class="['flex space-x-3 message-animation', message.isUser ? 'justify-end' : '']">
      <template v-if="!message.isUser">
        <div class="w-10 h-10 rounded-full bg-primary flex-shrink-0 overflow-hidden">
          <img :src="message.avatar" 
               :alt="message.sender" 
               class="w-full h-full object-cover">
        </div>
      </template>
      
      <div :class="['max-w-[80%]', message.isUser ? 'order-first' : '']">
        <div :class="[
          'p-4 rounded-xl shadow-sm',
          message.isUser 
            ? 'bg-primary text-white rounded-tr-none' 
            : 'bg-white rounded-tl-none'
        ]">
          <p>{{ message.content }}</p>
        </div>
        <div :class="[
          'text-xs text-gray-500 mt-1',
          message.isUser ? 'text-right' : ''
        ]">{{ message.time }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Message {
  content: string
  isUser: boolean
  sender: string
  avatar: string
  time: string
}

const messages = ref<Message[]>([
  {
    content: '您好！我是邹韬奋的数字人文形象。很高兴能与您交流。作为民国时期的报人和出版家，我创办了《生活》周刊和生活书店，致力于传播进步思想和科学知识。您有什么想了解的吗？',
    isUser: false,
    sender: '邹韬奋',
    avatar: 'https://ai-public.mastergo.com/ai/img_res/6557c05fa764370bbfe534180f301e0c.jpg',
    time: '上午 10:23'
  },
  {
    content: '邹先生您好！我对您创办的生活书店很感兴趣，能请您谈谈创办的初衷和过程吗？',
    isUser: true,
    sender: '用户',
    avatar: '',
    time: '上午 10:25'
  }
])
</script> 