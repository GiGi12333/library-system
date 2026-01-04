import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import bcrypt from '../utils/bcrypt'

export const useUserStore = defineStore('user', () => {
  // 状态
  const currentUser = ref(JSON.parse(localStorage.getItem('currentUser') || 'null'))
  const users = ref(JSON.parse(localStorage.getItem('users') || '[]'))

  // 初始化管理员账户
  if (users.value.length === 0) {
    const adminUser = {
      id: 1,
      username: 'admin',
      password: bcrypt.hash('admin123'),
      role: 'admin',
      name: '系统管理员',
      email: 'admin@library.com',
      phone: '13800000000',
      createTime: new Date().toISOString()
    }
    users.value.push(adminUser)
    localStorage.setItem('users', JSON.stringify(users.value))
  }

  // 计算属性
  const isLoggedIn = computed(() => !!currentUser.value)
  const isAdmin = computed(() => currentUser.value?.role === 'admin')

  // 方法
  function login(username, password) {
    const user = users.value.find(u => u.username === username)
    if (!user) {
      throw new Error('用户不存在')
    }
    if (!bcrypt.verify(password, user.password)) {
      throw new Error('密码错误')
    }
    currentUser.value = { ...user, password: undefined }
    localStorage.setItem('currentUser', JSON.stringify(currentUser.value))
    return currentUser.value
  }

  function register(userData) {
    if (users.value.find(u => u.username === userData.username)) {
      throw new Error('用户名已存在')
    }
    const newUser = {
      id: users.value.length + 1,
      ...userData,
      password: bcrypt.hash(userData.password),
      role: 'user',
      createTime: new Date().toISOString()
    }
    users.value.push(newUser)
    localStorage.setItem('users', JSON.stringify(users.value))
    return newUser
  }

  function logout() {
    currentUser.value = null
    localStorage.removeItem('currentUser')
  }

  function getAllUsers() {
    return users.value.map(u => ({ ...u, password: undefined }))
  }

  function updateUser(id, data) {
    const index = users.value.findIndex(u => u.id === id)
    if (index === -1) throw new Error('用户不存在')
    users.value[index] = { ...users.value[index], ...data }
    if (data.password) {
      users.value[index].password = bcrypt.hash(data.password)
    }
    localStorage.setItem('users', JSON.stringify(users.value))
    return users.value[index]
  }

  function deleteUser(id) {
    const index = users.value.findIndex(u => u.id === id)
    if (index === -1) throw new Error('用户不存在')
    if (users.value[index].role === 'admin') throw new Error('不能删除管理员')
    users.value.splice(index, 1)
    localStorage.setItem('users', JSON.stringify(users.value))
  }

  return {
    currentUser,
    users,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout,
    getAllUsers,
    updateUser,
    deleteUser
  }
})
