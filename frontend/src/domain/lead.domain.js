export const leadDomain = {
  /**
   * Проверяет корректность заполнения полей формы перед отправкой
   * @param {string} name 
   * @param {string} phone 
   * @param {boolean} agreedToTerms 
   * @returns {{isValid: boolean, error: string | null}}
   */
  validateForm(name, phone, agreedToTerms) {
    if (!name.trim()) {
      return { isValid: false, error: 'Пожалуйста, введите ваше имя.' }
    }
    if (!phone.trim()) {
      return { isValid: false, error: 'Пожалуйста, введите ваш номер телефона.' }
    }
    if (!agreedToTerms) {
      return { isValid: false, error: 'Необходимо согласиться на обработку персональных данных.' }
    }
    return { isValid: true, error: null }
  }
}