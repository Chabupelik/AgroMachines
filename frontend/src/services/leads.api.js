import api from './api'

export const leadsApi = {
  async createLead(name, phone, captchaToken) {
    const res = await api.post('/api/v1/leads/', {
      client_name: name,
      client_phone: phone,
      captcha_token: captchaToken
    })
    return res.data
  },

  async getLeads(limit = 20, offset = 0) {
    const res = await api.get('/api/v1/leads/', {
      params: { limit, offset }
    })
    return res.data
  },

  async updateStatus(leadId, newStatus) {
    const res = await api.put(`/api/v1/leads/${leadId}`, null, {
      params: { new_status: newStatus }
    })
    return res.data
  },

  async deleteLead(leadId) {
    const res = await api.delete(`/api/v1/leads/${leadId}`)
    return res.data
  }
}