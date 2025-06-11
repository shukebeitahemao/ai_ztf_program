<template>
  <aside class="w-[240px] bg-white border-r border-gray-200 flex flex-col h-[calc(100vh-60px)] sidebar-transition">
    <div class="p-4 border-b border-gray-200">
      <button class="w-full bg-primary hover:bg-secondary text-white py-2 px-4 !rounded-button whitespace-nowrap" @click="createNewChat">
        <i class="fas fa-plus mr-2"></i> 新对话
      </button>
    </div>
    
    <div class="flex-1 overflow-y-auto">
      <div v-for="(group, index) in chatGroups" :key="index" class="p-4 space-y-2">
        <div class="text-sm text-gray-500 mb-2">{{ group.title }}</div>
        
        <button v-for="chat in group.chats" 
                :key="chat.id"
                class="w-full text-left p-2 rounded hover:bg-gray-100 transition-colors flex items-center"
                @click="selectChat(chat.id)">
          <i class="fas fa-comment-dots text-gray-400 mr-2"></i>
          <span class="truncate">{{ chat.title }}</span>
        </button>
      </div>
    </div>
    
    <div class="p-4 border-t border-gray-200">
      <button class="text-gray-500 hover:text-primary transition-colors flex items-center" @click="toggleSidebar">
        <i class="fas fa-chevron-left mr-2"></i>
        <span>收起边栏</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Chat {
  id: number
  title: string
}

interface ChatGroup {
  title: string
  chats: Chat[]
}

const chatGroups = ref<ChatGroup[]>([
  {
    title: '今天',
    chats: [
      { id: 1, title: '关于生活书店的创办历程' },
      { id: 2, title: '七君子事件的详细经过' },
      { id: 3, title: '邹韬奋的英语学习方法' }
    ]
  },
  {
    title: '昨天',
    chats: [
      { id: 4, title: '《生活》周刊的编辑理念' },
      { id: 5, title: '邹韬奋的少年时代' }
    ]
  },
  {
    title: '更早',
    chats: [
      { id: 6, title: '职业选择与人生规划' },
      { id: 7, title: '邹韬奋的新闻思想' }
    ]
  }
])

const createNewChat = () => {
  // 实现创建新对话的逻辑
}

const selectChat = (chatId: number) => {
  // 实现选择对话的逻辑
}

const toggleSidebar = () => {
  // 实现收起/展开侧边栏的逻辑
}
</script> 