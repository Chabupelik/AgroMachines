// src/domain/user.domain.js
import { ROLES } from '@/constants/roles'

export const userDomain = {

  validateForm(username, password, role, isEditMode = false) {
    const usernameRegex = /^[a-zA-Z0-9_]+$/
    
    if (!username || !username.trim()) {
      return { isValid: false, error: 'Имя пользователя (логин) обязательно.' }
    }
    if (!usernameRegex.test(username.trim())) {
      return { isValid: false, error: 'Логин должен состоять только из латинских букв, цифр и знака подчеркивания.' }
    }
    if (username.trim().length < 3) {
      return { isValid: false, error: 'Логин должен быть не короче 3 символов.' }
    }

    if (!isEditMode && (!password || password.trim().length < 6)) {
      return { isValid: false, error: 'Пароль обязателен и должен содержать не менее 6 символов.' }
    }
    if (isEditMode && password && password.trim().length < 6) {
      return { isValid: false, error: 'Новый пароль должен содержать не менее 6 символов.' }
    }

    if (!role) {
      return { isValid: false, error: 'Пожалуйста, выберите роль доступа.' }
    }

    return { isValid: true, error: null }
  },

  canEditUser(targetUser, currentUser) {
    if (!currentUser) return false
    
    if (targetUser.id === currentUser.id) return true
    
    if (targetUser.role === ROLES.SUPERADMIN) return false
    
    return true
  },

  canDeleteUser(targetUser, currentUser) {
    if (!currentUser) return false
    
    if (targetUser.id === currentUser.id) return false
    
    if (targetUser.role === ROLES.SUPERADMIN) return false
    
    return true
  }
}