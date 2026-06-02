export const config = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
  siteUrl: import.meta.env.VITE_SITE_URL || "agromachines.chabupelik.su",
  siteName: import.meta.env.VITE_SITE_NAME || "AgroMachines",
  companyName: import.meta.env.VITE_COMPANY_NAME || 'ООО "АгроТехника"',
  companyInn: import.meta.env.VITE_COMPANY_INN || "1234567890",
  companyOgrn: import.meta.env.VITE_COMPANY_OGRN || "1234567890123",
  companyAddress: import.meta.env.VITE_COMPANY_ADDRESS || "г. Москва, ул. Полевая, д. 45, офис 12",
  supportPhone: import.meta.env.VITE_SUPPORT_PHONE || "+7 (999) 000-00-00",
  supportEmail: import.meta.env.VITE_SUPPORT_EMAIL || "support@agromachines.chabupelik.su",
  telegramLink: import.meta.env.VITE_TELEGRAM_LINK || "https://t.me/agromachines",
  policyUpdatedAt: import.meta.env.VITE_POLICY_UPDATED_AT || "02 июня 2026",
  turnstileSiteKey: import.meta.env.VITE_TURNSTILE_SITE_KEY || "1x000000000000000000001A", 
}