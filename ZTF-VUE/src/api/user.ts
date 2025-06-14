import axios from 'axios'

const API_BASE_URL = 'http://localhost:3000' // 根据实际后端地址修改

export const sendUserUID = async (uid: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/user`, { uid })
    console.log('生成的用户ID:', uid)
    console.log('服务器响应:', response.data)
    return response.data
  } catch (error) {
    console.error('发送用户ID失败:', error)
    throw error
  }
}
