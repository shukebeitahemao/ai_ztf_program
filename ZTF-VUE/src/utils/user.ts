const UID_KEY = 'ztf_user_uid'

export const generateUID = (): string => {
  return 'uid_' + Math.random().toString(36).substr(2, 9)
}

export const getOrCreateUID = (): string => {
  let uid = localStorage.getItem(UID_KEY)
  if (!uid) {
    uid = generateUID()
    localStorage.setItem(UID_KEY, uid)
  }
  return uid
}
