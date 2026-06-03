import api from './api'

export const machinesApi = {
  async getMachines(limit = 12, offset = 0) {
    const res = await api.get('/api/v1/machines/', { params: { limit, offset } })
    return res.data
  },

  async createMachine(machineData, filesArray) {
    const formData = new FormData()
    formData.append('title', machineData.title)
    if (machineData.description) formData.append('description', machineData.description)
    if (machineData.price) formData.append('price', machineData.price)
    
    formData.append('specifications', JSON.stringify(machineData.specifications || {}))
    formData.append('is_available', machineData.is_available)
    
    if (filesArray && filesArray.length > 0) {
      filesArray.forEach(file => formData.append('files', file))
    }

    const res = await api.post('/api/v1/machines/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return res.data
  },

  async updateMachine(id, machineData, filesArray) {
    const formData = new FormData()
    formData.append('title', machineData.title)
    if (machineData.description) formData.append('description', machineData.description)
    if (machineData.price) formData.append('price', machineData.price)
    
    formData.append('specifications', JSON.stringify(machineData.specifications || {}))
    formData.append('is_available', machineData.is_available)
    
    if (machineData.image_urls) {
      formData.append('existing_image_urls', JSON.stringify(machineData.image_urls))
    }

    if (filesArray && filesArray.length > 0) {
      filesArray.forEach(file => formData.append('files', file))
    }

    const res = await api.put(`/api/v1/machines/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return res.data
  },

  async deleteMachine(id) {
    const res = await api.delete(`/api/v1/machines/${id}`)
    return res.data
  }
}