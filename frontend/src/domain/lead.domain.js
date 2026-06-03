export const leadDomain = {
  
  validateForm(name, phone, agreedToTerms) {
    if (!name.trim()) return { isValid: false, error: 'Пожалуйста, введите ваше имя.' }
    if (!phone.trim()) return { isValid: false, error: 'Пожалуйста, введите ваш номер телефона.' }
    if (!agreedToTerms) return { isValid: false, error: 'Необходимо согласиться на обработку персональных данных.' }
    return { isValid: true, error: null }
  },

  canTakeInProgress(lead) {
    return lead.status === 'NEW' && !lead.processed_by
  },


  canComplete(lead, currentUsername, userRole) {
    if (lead.status !== 'IN_PROGRESS') return false
    
    if (userRole === 'SUPERADMIN') return true
    
    return lead.processed_by === currentUsername
  }
}