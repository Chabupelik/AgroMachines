import api from './api'

export const authApi = {
  async login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const res = await api.post('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return res.data
  },

  async logout() {
    const res = await api.post('/api/v1/auth/logout')
    return res.data
  },

  async getUsers() {
    const res = await api.get('/api/v1/auth/users')
    return res.data
  }
}