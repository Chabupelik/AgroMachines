export const mapApiError = (error) => {
  if (!error.response) {
    return "Сеть недоступна. Проверьте интернет-соединение."
  }

  const status = error.response.status
  const data = error.response.data

  if (status === 401) {
    return "Неверный логин или пароль, либо сессия истекла."
  }
  if (status === 403) {
    return "Доступ заблокирован. Недостаточно прав для действия."
  }
  if (status === 404) {
    return "Запрашиваемые данные не найдены на сервере."
  }
  if (status === 429) {
    return "Слишком много запросов. Пожалуйста, попробуйте через минуту."
  }
  if (status === 409) {
    return data?.message || "Конфликт данных в базе."
  }

  return data?.message || "Произошла непредвиденная ошибка на сервере."
}