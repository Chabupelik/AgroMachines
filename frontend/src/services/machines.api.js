import api from './api'

export const machinesApi = {
  async getMachines(limit = 12, offset = 0) {
    const res = await api.get('/api/v1/machines/', {
      params: { limit, offset }
    })
    return res.data
  }
}