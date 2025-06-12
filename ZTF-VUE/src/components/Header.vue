<template>
  <header class="bg-white shadow-sm fixed top-0 left-0 right-0 z-50 h-[60px] flex items-center px-4">
    <div class="flex items-center justify-between w-full">
      <div class="flex items-center">
        <router-link to="/" class="font-['Pacifico'] text-xl text-primary">韬奋数字人文</router-link>
      </div>

      <nav class="hidden md:flex items-center space-x-6">
        <router-link to="/" class="text-gray-600 hover:text-primary transition-colors">首页</router-link>
        <router-link to="/chat" class="text-primary font-medium">对话邹韬奋</router-link>
        <router-link to="/" class="text-gray-600 hover:text-primary transition-colors">认识邹韬奋</router-link>
        <router-link to="/" class="text-gray-600 hover:text-primary transition-colors">漫画邹韬奋</router-link>
        <router-link to="/" class="text-gray-600 hover:text-primary transition-colors">韬奋时评</router-link>
        <router-link to="/" class="text-gray-600 hover:text-primary transition-colors">韬奋知识图谱</router-link>
      </nav>

      <button class="md:hidden text-gray-600" @click="toggleMobileMenu">
        <i class="fas fa-bars text-xl"></i>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}
</script>