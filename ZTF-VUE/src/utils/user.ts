import { sendUserUID } from '../api/ftbAPI'

const UID_KEY = 'ztf_user_uid'

/**
 * 生成用户ID
 * @returns Promise - 返回用户ID
 */
export const generateUID = async (): Promise<string> => {
  const uid = 'uid_' + Math.random().toString(36).substr(2, 9)
  //await sendUserUID(uid)
  return uid
}

/**
 * 获取或创建用户ID
 * @returns Promise - 返回用户ID
 */
export const getOrCreateUID = async (): Promise<string> => {
  let uid = localStorage.getItem(UID_KEY)
  if (!uid) {
    uid = await generateUID()
    //获取到的uid存到本地
    localStorage.setItem(UID_KEY, uid)
    //传输uid到后端
    await sendUserUID(uid)
  }
  return uid
}
