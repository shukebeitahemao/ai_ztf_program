<script setup lang="ts">
//import { RouterLink, RouterView } from 'vue-router'
//import HelloWorld from './components/HelloWorld.vue'
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
import ChatHeader from './components/ChatHeader.vue'
import ChatContainer from './components/ChatContainer.vue'
import ChatInput from './components/ChatInput.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <Header />
    <div class="flex flex-1 pt-[60px]">
      <Sidebar />
      <main class="flex-1 flex flex-col bg-paper">
        <ChatHeader />
        <ChatContainer />
        <div class="mt-auto pb-6 px-6">
          <ChatInput />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}

:root {
  --color-paper: #F3EFE8;
  --color-ink: #333333;
  --color-primary: #7D0013;
  --color-secondary: #9A2C3D;
}

body {
  font-family: 'Noto Sans SC', sans-serif;
  background-color: var(--color-paper);
  color: var(--color-ink);
}

.message-animation {
  animation: messageFadeIn 0.3s ease-out;
}

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.wave-animation {
  animation: wave 1.5s infinite ease-in-out;
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(0.6);
  }
  50% {
    transform: scaleY(1.2);
  }
}

.sidebar-transition {
  transition: transform 0.3s ease;
}

.chat-container {
  scroll-behavior: smooth;
}

.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}
</style>
