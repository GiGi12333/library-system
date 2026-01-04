// 简化的密码哈希工具（前端演示用）
// 实际生产环境应使用后端bcrypt库

const SALT = 'library_system_salt_2024'

function simpleHash(str) {
  let hash = 0
  const combined = str + SALT
  for (let i = 0; i < combined.length; i++) {
    const char = combined.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return 'hashed_' + Math.abs(hash).toString(16)
}

export default {
  hash(password) {
    return simpleHash(password)
  },
  verify(password, hashedPassword) {
    return simpleHash(password) === hashedPassword
  }
}
