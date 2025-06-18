import axios from 'axios'

const API_BASE_URL = 'http://localhost:3000'

interface CreateUserResponse {
  user_id: string;
}

interface CreateSessionResponse {
  user_id: string;
  session_id: string;
}

interface SendMessageResponse {
  sessionid: string;
  system_msg: string;
}
/**
 * 加载特定会话的历史记录
 * 功能：根据会话ID和用户ID加载特定会话的历史记录
 * 参数：
 *   - user_id: 用户ID
 *   - session_id: 会话ID
 * 返回值：
 *   - Promise<LoadSessionResponse>: 返回会话历史记录
 */
interface LoadSessionResponse {
  msg: [{
    user_id: string;
    session_id: string;
    history: string;
  }]
}

interface HistorySession {
  session_id: string;
  abstract: string;
  update_time: string;
}

interface LoadHistoryResponse {
  msg: HistorySession[];
}

interface DeleteSessionResponse {
  msg: string;
}

interface SaveUserMsgResponse {
  msg: string;
}

/**
 * 获取用户ID
 * 功能：从本地storage获取用户ID，如果不存在则从后端获取新的用户ID
 * 返回值：
 *   - Promise<string>: 返回用户ID
 * 错误处理：
 *   - 捕获并记录获取失败错误
 */
export const getUserId = async (): Promise<string> => {
  const STORAGE_KEY = 'ztf_user_id'
  try {
    // 检查本地storage中是否存在用户ID
    /* 正式环境
    const storedUserId = localStorage.getItem(STORAGE_KEY)
    */
    // 测试环境
    let storedUserId = localStorage.getItem(STORAGE_KEY)
    // 测试用：设置默认值
    storedUserId = '123'

    if (storedUserId) {
      return storedUserId
    }
    // 如果本地没有用户ID，从后端获取新的用户ID
    const response = await axios.get<CreateUserResponse>(`${API_BASE_URL}/create_user`)
    const { user_id } = response.data

    // 将新的用户ID保存到本地storage
    localStorage.setItem(STORAGE_KEY, user_id)
    return user_id
  } catch (error) {
    console.error('获取用户ID失败:', error)
    throw error
  }
}

/**
 * 创建新的会话
 * 功能：创建新的聊天会话，获取会话ID
 * 参数：
 *   - user_id: 用户ID
 * 返回值：
 *   - Promise<CreateSessionResponse>: 返回用户ID和会话ID
 */
export const createNewSession = async (user_id: string): Promise<CreateSessionResponse> => {
  const STORAGE_KEY = 'ztf_session_id'

  try {
    /* 正式环境
    const response = await axios.get<CreateSessionResponse>(`${API_BASE_URL}/chat/create_new_chat`, {
      params: {
        user_id
      }
    })

    // 将会话ID保存到本地storage
    localStorage.setItem(STORAGE_KEY, response.data.session_id)
    return response.data
    */

    // 测试环境
    const testSessionId = `session_${Date.now()}`
    const testResponse: CreateSessionResponse = {
      user_id: user_id,
      session_id: testSessionId
    }

    // 将会话ID保存到本地storage
    localStorage.setItem(STORAGE_KEY, testResponse.session_id)
    return testResponse

  } catch (error) {
    console.error('创建会话失败:', error)
    throw error
  }
}

/**
 * 发送消息到后端
 * 功能：发送用户消息并获取系统回复
 * 参数：
 *   - user_msg: 用户输入的消息内容
 *   - session_id: 当前会话ID
 *   - user_id: 用户ID
 *   - story_type: 话题类型（可选）
 * 返回值：
 *   - Promise<SendMessageResponse>: 返回会话ID和系统回复
 */
export const sendMessage = async (
  user_msg: string,
  session_id: string,
  user_id: string,
  story_type: string = ''
): Promise<SendMessageResponse> => {
  try {
    /* 正式环境
    const response = await axios.get<SendMessageResponse>(`${API_BASE_URL}/chat`, {
      params: {
        user_id,
        session_id,
        user_msg,
        story_type
      }
    })
    return response.data
    */

    // 测试环境
    // 模拟后端响应
    const testResponse: SendMessageResponse = {
      sessionid: session_id,
      system_msg: `测试回复: 收到消息"${user_msg}"，会话ID为${session_id}${story_type ? '，话题为' + story_type : ''}`
    }
    return testResponse

  } catch (error) {
    console.error('发送消息失败:', error)
    throw error
  }
}

/**
 * 加载特定会话的历史记录
 * 功能：根据会话ID和用户ID加载特定会话的历史记录
 * 参数：
 *   - user_id: 用户ID
 *   - session_id: 会话ID
 * 返回值：
 *   - Promise<LoadSessionResponse>: 返回会话历史记录
 */
export const loadSpecificSession = async (
  user_id: string,
  session_id: string
): Promise<LoadSessionResponse> => {
  try {
    /* 正式环境
    const response = await axios.get<LoadSessionResponse>(`${API_BASE_URL}/load_specific_session`, {
      params: {
        user_id,
        session_id
      }
    })
    return response.data
    */

    // 测试环境
    // 模拟后端响应
    const testResponse: LoadSessionResponse = {
      msg: [{
        user_id: user_id,
        session_id: session_id,
        history: JSON.stringify([
          { role: 'user', content: '测试消息1' },
          { role: 'assistant', content: '测试回复1' },
          { role: 'user', content: '测试消息2' },
          { role: 'assistant', content: '测试回复2' }
        ])
      }]
    }
    return testResponse

  } catch (error) {
    console.error('加载会话历史记录失败:', error)
    throw error
  }
}

/**
 * 加载用户历史会话记录
 */
export const loadHistory = async (user_id: string): Promise<LoadHistoryResponse> => {
  try {
    /* 正式环境
    const response = await axios.get<LoadHistoryResponse>(`${API_BASE_URL}/load_history`, {
      params: { user_id }
    })
    return response.data
    */

    // 测试环境
    return {
      msg: [
        {
          session_id: 'test_session_1',
          abstract: '邹韬奋的教育理念探讨',
          update_time: '2024-03-11T10:00:00Z'
        },
        {
          session_id: 'test_session_2',
          abstract: '关于生活书店的对话',
          update_time: '2024-03-11T09:00:00Z'
        }
      ]
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    throw error
  }
}

/**
 * 删除指定会话
 */
export const deleteSession = async (user_id: string, session_id: string): Promise<DeleteSessionResponse> => {
  try {
    /* 正式环境
    const response = await axios.post<DeleteSessionResponse>(`${API_BASE_URL}/chat/delete_session`, {
      user_id,
      session_id
    })
    return response.data
    */

    // 测试环境
    return {
      msg: "删除成功"
    }
  } catch (error) {
    console.error('删除会话失败:', error)
    throw error
  }
}

/**
 * 自动保存用户消息
 * 功能：在用户关闭页面或浏览器时自动保存用户消息
 * 参数：
 *   - user_id: 用户ID
 * 返回值：
 *   - Promise<SaveUserMsgResponse>: 返回保存状态信息
 */
export const saveUserMsg = async (user_id: string): Promise<SaveUserMsgResponse> => {
  try {
    const response = await axios.get<SaveUserMsgResponse>(`${API_BASE_URL}/chat/save_usermsg`, {
      params: {
        userid: user_id
      }
    })
    return response.data
  } catch (error) {
    console.error('保存用户消息失败:', error)
    throw error
  }
}


/**

 * 获取当前会话ID
 * 功能：从本地storage获取当前会话ID
 * 返回值：
 *   - string | null: 返回会话ID，如果不存在则返回null

export const getCurrentSessionId = (): string | null => {
  const STORAGE_KEY = 'ztf_session_id'
  return localStorage.getItem(STORAGE_KEY)
}

 * 创建新的聊天记录
 * 功能：创建新的聊天会话，并记录话题信息
 * 参数：
 *   - chatTitle: 聊天标题，格式为 uid_YYYYMMDD_HHMM
 *   - topic: 聊天话题，可选参数
 * 返回值：
 *   - Promise: 包含服务器响应数据
 * 错误处理：
 *   - 捕获并记录创建失败错误

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
*/