import axios from 'axios'

const API_BASE_URL = 'http://localhost:3000'

/**
 * 传输userUID到后端
 * 功能：用户首次访问时，向后端注册用户ID
 * 参数：
 *   - uid: 用户唯一标识符，格式为 'uid_' + 随机字符串
 * 返回值：
 *   - Promise: 包含服务器响应数据
 * 错误处理：
 *   - 捕获并记录注册失败错误
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

/**
 * 传输会话ID到后端，后端根据会话ID查询会话记录，并返回历史会话记录，如果会话记录不存在，则创建新的会话
 */

/**
 * 传输会话ID和删除指令到后端，后端针对会话ID删除历史会话记录
 */

/**
 * 创建新的聊天记录
 * 功能：创建新的聊天会话，并记录话题信息
 * 参数：
 *   - chatTitle: 聊天标题，格式为 uid_YYYYMMDD_HHMM
 *   - topic: 聊天话题，可选参数
 * 返回值：
 *   - Promise: 包含服务器响应数据
 * 错误处理：
 *   - 捕获并记录创建失败错误
 */
export const createNewChat = async (chatTitle: string, topic: string = '') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/chat/create_new_chat`, {
      params: {
        title: chatTitle,
        topic
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
 * 功能：发送用户消息并获取系统回复
 * 参数：
 *   - message: 用户输入的消息内容
 *   - chatId: 当前聊天会话ID
 *   - uid: 用户ID
 *   - timestamp: 消息发送时间
 * 返回值：
 *   - Promise: 包含服务器响应数据，其中reply字段为系统回复
 * 错误处理：
 *   - 捕获并记录发送失败错误
 * 说明：
 *   - 如果服务器没有返回reply，前端会显示默认消息"后端已收到您的消息"
 */
export const sendMessage = async (message: string, chatId: string, uid: string, timestamp: Date) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/chat/send_message`, {
      params: {
        message,
        chatId,
        uid,
        timestamp: timestamp.toISOString()
      }
    })
    return response.data
  } catch (error) {
    console.error('发送消息失败:', error)
    throw error
  }
}

