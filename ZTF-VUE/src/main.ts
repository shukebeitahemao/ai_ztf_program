import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
//
// import { getOrCreateUID } from './utils/user'

// 在应用启动时初始化用户UID
// getOrCreateUID()

const app = createApp(App)
app.use(router)
app.mount('#app')
