import axios from 'axios'

const API_BASE_URL = 'http://localhost:3000'

interface CreateUserResponse {
  userid: string;
}

interface CreateSessionResponse {
  userid: string;
  sessionid: string;
}

interface SendMessageResponse {
  sessionid: string;
  system_msg: string;
}
/**
 * 加载特定会话的历史记录
 * 功能：根据会话ID和用户ID加载特定会话的历史记录
 * 参数：
 *   - userid: 用户ID
 *   - sessionid: 会话ID
 * 返回值：
 *   - Promise<LoadSessionResponse>: 返回会话历史记录
 */
interface LoadSessionResponse {
  msg: [{
    userid: string;
    sessionid: string;
    history: string;
  }]
}

interface HistorySession {
  sessionid: string;
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
    // 正式环境
    const storedUserId = localStorage.getItem(STORAGE_KEY)

    // 测试环境
    //let storedUserId = localStorage.getItem(STORAGE_KEY)
    // 测试用：设置默认值
    //storedUserId = '123'

    if (storedUserId) {
      return storedUserId
    }
    // 如果本地没有用户ID，从后端获取新的用户ID
    const response = await axios.get<CreateUserResponse>(`${API_BASE_URL}/create_user`)
    const { userid } = response.data

    // 将新的用户ID保存到本地storage
    localStorage.setItem(STORAGE_KEY, userid)
    return userid
  } catch (error) {
    console.error('获取用户ID失败:', error)
    throw error
  }
}

/**
 * 创建新的会话
 * 功能：创建新的聊天会话，获取会话ID
 * 参数：
 *   - userid: 用户ID
 * 返回值：
 *   - Promise<CreateSessionResponse>: 返回用户ID和会话ID
 */
export const createNewSession = async (userid: string): Promise<CreateSessionResponse> => {
  const STORAGE_KEY = 'ztf_session_id'
  try {
    //正式环境
    const response = await axios.get<CreateSessionResponse>(`${API_BASE_URL}/chat/create_new_chat`, {
      params: {
        userid
      }
    })
    // 将会话ID保存到本地storage
    localStorage.setItem(STORAGE_KEY, response.data.sessionid)
    return response.data

    /*测试环境
    const testSessionId = `session_${Date.now()}`
    const testResponse: CreateSessionResponse = {
      userid: userid,
      sessionid: testSessionId
    }

    // 将会话ID保存到本地storage
    localStorage.setItem(STORAGE_KEY, testResponse.sessionid)
    return testResponse
*/

  } catch (error) {
    console.error('创建会话失败:', error)
    throw error
  }
}

/**
 * 获取当前会话ID
 * 功能：从本地storage获取当前会话ID
 * 返回值：
 *   - string | null: 返回会话ID，如果不存在则返回null
 */
export const getCurrentSessionId = (): string | null => {
  const STORAGE_KEY = 'ztf_session_id'
  return localStorage.getItem(STORAGE_KEY)
}

/**
 * 发送消息到后端
 * 功能：发送用户消息并获取系统回复
 * 参数：
 *   - user_msg: 用户输入的消息内容
 *   - sessionid: 当前会话ID
 *   - userid: 用户ID
 *   - story_type: 话题类型（可选）
 * 返回值：
 *   - Promise<SendMessageResponse>: 返回会话ID和系统回复
 */
export const sendMessage = async (
  user_msg: string,
  sessionid: string,
  userid: string,
  story_type: string = ''
): Promise<SendMessageResponse> => {
  try {
    // 正式环境
    const response = await axios.get<SendMessageResponse>(`${API_BASE_URL}/chat`, {
      params: {
        userid,
        sessionid,
        user_msg,
        story_type
      }
    })
    return response.data


    /* 测试环境
    // 模拟后端响应
    const testResponse: SendMessageResponse = {
      sessionid: sessionid,
      system_msg: `测试回复: 收到消息"${user_msg}"，会话ID为${sessionid}${story_type ? '，话题为' + story_type : ''}`
    }
    return testResponse
    */

  } catch (error) {
    console.error('发送消息失败:', error)
    throw error
  }
}

/**
 * 加载特定会话的历史记录
 * 功能：根据会话ID和用户ID加载特定会话的历史记录
 * 参数：
 *   - userid: 用户ID
 *   - sessionid: 会话ID
 * 返回值：
 *   - Promise<LoadSessionResponse>: 返回会话历史记录
 */
export const loadSpecificSession = async (
  userid: string,
  sessionid: string
): Promise<LoadSessionResponse> => {
  try {
    // 正式环境
    const response = await axios.get<LoadSessionResponse>(`${API_BASE_URL}/load_specific_session`, {
      params: {
        userid,
        sessionid
      }
    })
    return response.data

/*
    // 测试环境
    // 模拟后端响应
    const testResponse: LoadSessionResponse = {
      msg: [{
        userid: userid,
        sessionid: sessionid,
        history: JSON.stringify([
          { role: 'user', content: '测试消息1' },
          { role: 'assistant', content: '测试回复1' },
          { role: 'user', content: '测试消息2' },
          { role: 'assistant', content: '测试回复2' }
        ])
      }]
    }
    return testResponse
*/
  } catch (error) {
    console.error('加载会话历史记录失败:', error)
    throw error
  }
}

/**
 * 加载历史记录
 * 功能：加载用户的历史会话记录
 * 参数：
 *   - userid: 用户ID
 * 返回值：
 *   - Promise: 包含历史会话记录的响应
 */
export const loadHistory = async (userid: string): Promise<LoadHistoryResponse> => {
  try {
    // 正式环境
    const response = await axios.get<LoadHistoryResponse>(`${API_BASE_URL}/chat/load_history`, {
      params: { userid }
    })
    return response.data


    /* 测试环境
    // 模拟后端响应
    const testResponse = {
      msg: [
        {
          sessionid: 'test_session_1',
          abstract: '测试会话1',
          update_time: new Date().toISOString()
        },
        {
          sessionid: 'test_session_2',
          abstract: '测试会话2',
          update_time: new Date(Date.now() - 86400000).toISOString() // 一天前
        }
      ]
    }
    return testResponse*/

  } catch (error) {
    console.error('加载历史记录失败:', error)
    throw error
  }
}

/**
 * 删除会话
 * 功能：删除指定的会话记录
 * 参数：
 *   - userid: 用户ID
 *   - sessionid: 会话ID
 * 返回值：
 *   - Promise: 包含删除操作的响应
 */
export const deleteSession = async (userid: string, sessionid: string): Promise<DeleteSessionResponse> => {
  try {
    // 正式环境
    const response = await axios.delete<DeleteSessionResponse>(`${API_BASE_URL}/chat/delete_session`, {
      params: {
        userid,
        sessionid
      }
    })
    return response.data


    // 测试环境
    // 模拟后端响应
    //return { msg: 'success' }

  } catch (error) {
    console.error('删除会话失败:', error)
    throw error
  }
}

/**
 * 保存用户消息
 * 功能：保存用户的消息到后端
 * 参数：
 *   - userid: 用户ID
 * 返回值：
 *   - Promise<SaveUserMsgResponse>: 返回保存结果
 */
export const saveUserMsg = async (userid: string): Promise<SaveUserMsgResponse> => {
  try {
    // 正式环境
    const response = await axios.get<SaveUserMsgResponse>(`${API_BASE_URL}/chat/save_user_msg`, {
      params: {
        userid
      }
    })
    return response.data


    // 测试环境
    //const testResponse: SaveUserMsgResponse = {
    //  msg: '保存成功'
    //}
    //return testResponse
  } catch (error) {
    console.error('保存用户消息失败:', error)
    throw error
  }
}

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
