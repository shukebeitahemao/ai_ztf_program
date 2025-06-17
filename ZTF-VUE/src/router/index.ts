import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChatAI from '../views/ChatAI.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatAI
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// 确保首次访问时打开首页
router.beforeEach((to, from, next) => {
  if (to.path === '/') {
    // 如果是首次访问，确保显示首页
    next()
  } else {
    next()
  }
})

export default router
