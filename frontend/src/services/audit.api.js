import api from './api'

export const auditApi = {
  async getLogs(limit = 30, offset = 0, filters = {}) {
    const res = await api.get('/api/v1/audit/', {
      params: { limit, offset, ...filters }
    })
    return res.data
  }
}