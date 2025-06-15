import { sendUserUID } from '../api/ftbAPI'

const UID_KEY = 'ztf_user_uid'

export const generateUID = async (): Promise<string> => {
  const uid = 'uid_' + Math.random().toString(36).substr(2, 9)
  await sendUserUID(uid)
  return uid
}

export const getOrCreateUID = async (): Promise<string> => {
  let uid = localStorage.getItem(UID_KEY)
  if (!uid) {
    uid = await generateUID()
    localStorage.setItem(UID_KEY, uid)
  }
  return uid
}
