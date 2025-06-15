import axios from 'axios'

const API_BASE_URL = 'http://localhost:3000'

/**传输userUID到后端 */

/**传输会话ID到后端，后端根据会话ID查询会话记录，并返回历史会话记录，如果会话记录不存在，则创建新的会话 */

/**传输会话ID和删除指令到后端，后端针对会话ID删除历史会话记录 */
/**
 * 创建新的聊天记录
 * @param chatTitle - 聊天标题，格式为：uid_YYYYMMDD_HHMM
 * @returns Promise - 返回服务器响应数据
 */
export const createNewChat = async (chatTitle: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/chat/create_new_chat`, {
      params: {
        title: chatTitle
      }
    })
    return response.data
  } catch (error) {
    console.error('创建聊天记录失败:', error)
    throw error
  }
}

/**
 * 发送用户消息到后端
 * @param message - 消息内容
 * @param chatId - 聊天ID
 * @param uid - 用户ID
 * @returns Promise - 返回服务器响应数据
 */
export const sendMessage = async (message: string, chatId: string, uid: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/chat/send_message`, {
      params: {
        message,
        chatId,
        uid
      }
    })
    return response.data
  } catch (error) {
    console.error('发送消息失败:', error)
    throw error
  }
}

/**
 * 传输userUID到后端
 * @param uid - 用户唯一标识符
 * @returns Promise - 返回服务器响应数据
 */
export const sendUserUID = async (uid: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/register`, {
      params: {
        uid
      }
    })
    return response.data
  } catch (error) {
    console.error('注册用户失败:', error)
    throw error
  }
}
