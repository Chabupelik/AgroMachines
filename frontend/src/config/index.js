export const config = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
  siteName: import.meta.env.VITE_SITE_NAME || "AgroMachines PRO",
  companyName: import.meta.env.VITE_COMPANY_NAME || 'ООО "АгроТехника"',
  companyInn: import.meta.env.VITE_COMPANY_INN || "1234567890",
  companyOgrn: import.meta.env.VITE_COMPANY_OGRN || "1234567890123",
  supportPhone: import.meta.env.VITE_SUPPORT_PHONE || "+7 (999) 000-00-00",
  telegramLink: import.meta.env.VITE_TELEGRAM_LINK || "https://t.me/agromachines",
  turnstileSiteKey: import.meta.env.VITE_TURNSTILE_SITE_KEY || "1x000000000000000000001A", 
}