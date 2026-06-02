import api from './api'

export const leadsApi = {
  async createLead(name, phone, captchaToken) {
    const res = await api.post('/api/v1/leads/', {
      client_name: name,
      client_phone: phone,
      captcha_token: captchaToken
    })
    return res.data 
  }
}