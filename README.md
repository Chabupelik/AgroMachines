# 🌾 AgroMachines — Fullstack-платформа каталога сельхозтехники

**AgroMachines** — это production-ready веб-платформа для продажи и аренды сельскохозяйственной техники с публичным каталогом, системой заявок и полноценной панелью администратора.

Ключевые особенности: интеграция с Telegram-ботом для управления заявками в реальном времени, многоуровневая безопасность API (JWT + HttpOnly Cookie + RBAC), S3-хранилище медиафайлов через MinIO и защита от дублей/спама на уровне БД и Redis.

---

## 🎯 1. Архитектура и концепция

Платформа решает задачу цифровизации продаж сельхозтехники: клиент видит каталог с фото и характеристиками, оставляет заявку — менеджер мгновенно получает её в Telegram и может обработать прямо из бота.

1. **Публичный каталог (Vue 3 SPA):** Фронтенд отображает карточки техники с фото, спецификациями и ценой. Весь статический бандл раздаётся через Nginx напрямую.
2. **Система заявок с защитой от дублей:** При отправке формы обратного звонка бэкенд проверяет наличие активной заявки по номеру телефона (на уровне кода + частичный уникальный индекс PostgreSQL для защиты от race condition).
3. **Telegram-интеграция:** Новые заявки мгновенно уходят менеджерам в чат с Inline-кнопками «Взять в работу» / «Завершить». Нажатие кнопки — webhook на бэкенд, обновление статуса в БД и редактирование сообщения в Telegram.
4. **Полноценная Admin Panel:** Защищённый SPA для управления каталогом техники, заявками и пользователями с ролевой моделью (SUPERADMIN / EDITOR / MANAGER) и журналом аудита.

---

## 🏗 2. Архитектура и сетевой стек

Проект разделён на два контура: **Frontend (Vue 3 SPA)** и **Backend (Python / FastAPI)**.

### Схема запроса
`Браузер клиента` → `Cloudflare CDN` → `Nginx (reverse proxy)` → `FastAPI (Python)` → `PostgreSQL / Redis / MinIO`

1. **Nginx:** Раздаёт статику Vue 3, проксирует `/api/` на FastAPI и `/media/` на MinIO. Порты MinIO наружу не открываются.
2. **FastAPI (Async):** Асинхронный API на Python с SQLAlchemy 2.0 + asyncpg. Все тяжёлые операции (отправка в Telegram) выполняются через BackgroundTasks, не блокируя ответ клиенту.
3. **PostgreSQL + Redis + MinIO:** Основная БД, кэш/локи/rate-limit и S3-хранилище фото соответственно.

### Схема базы данных (PostgreSQL)

| Таблица | Назначение |
|---|---|
| `users` | Администраторы с ролями (UUID PK, Argon2id хэш пароля, RBAC роль) |
| `machines` | Карточки техники (JSONB спецификации, массив image_urls, цена Numeric) |
| `leads` | Заявки клиентов (статус NEW/IN_PROGRESS/DONE, частичный уникальный индекс по телефону) |
| `audit_logs` | Журнал действий администраторов (user_id FK, action, entity_type, timestamp) |

---

## 🛡 3. Безопасность

### Авторизация (JWT + Rolling Refresh)
- **Access Token** (15 мин) — возвращается в JSON, хранится в Pinia (RAM). Никакого localStorage.
- **Refresh Token** (7 дней) — записывается в `HttpOnly; Secure; SameSite=Strict` cookie. Недоступен из JS.
- **Rolling Refresh:** каждый `/api/refresh` перевыпускает оба токена, сдвигая срок жизни. Активный пользователь никогда не разлогинивается.
- **Argon2id:** пароли администраторов хранятся с хэшированием, рекомендованным OWASP.

### Защита публичных форм
- **Cloudflare Turnstile:** капча проверяется на стороне бэкенда перед записью заявки.
- **Rate Limiting (Redis, Token Bucket):** ограничение по IP и маскам подсети.
- **Валидация телефона:** библиотека `phonenumbers` (порт Google Libphonenumber) — проверка не только формата, но и существования кода страны/оператора.
- **XSS-санитаризация:** удаление HTML-тегов из текстовых полей на уровне Pydantic-схемы.

### Защита от гонок состояний
- **Race condition в заявках:** атомарный `UPDATE ... WHERE status = 'NEW'` — если 0 строк затронуто, бэкенд возвращает конфликт.
- **Частичный индекс PostgreSQL:** `CREATE UNIQUE INDEX uniq_active_phone ON leads(client_phone) WHERE status IN ('NEW', 'IN_PROGRESS')` — физически исключает дублирование на уровне СУБД.

---

## 💻 4. Стек технологий

| Слой | Технологии |
|---|---|
| **Frontend** | Vue 3, Vite, Pinia, Tailwind CSS / Vanilla CSS |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL (основная БД), Redis (кэш, rate limit, локи) |
| **Media Storage** | MinIO (S3-совместимое локальное хранилище, boto3) |
| **Auth** | JWT (python-jose), Argon2id (argon2-cffi) |
| **Infrastructure** | Docker, Docker Compose, Nginx, Cloudflare |
| **Integrations** | Telegram Bot API, Cloudflare Turnstile |

---

## ⚙️ 5. Запуск и сборка

### Требования
- **Сервер:** Linux VPS, Docker & Docker Compose, Node.js 18+
- **Локально:** Python 3.12+, Node.js 18+, Docker Desktop

### Настройка окружения

1. Скопируйте шаблон `.env` и заполните секреты:
   ```bash
   cp .env.example .env
   ```

   Ключевые переменные:
   ```env
   POSTGRES_USER=agroprom_admin
   POSTGRES_PASSWORD=<strong_password>
   POSTGRES_DB=agroprom_db

   SECRET_KEY=<64-char-random-string>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7

   TG_BOT_TOKEN=<your_bot_token>
   TG_CHAT_ID=<your_chat_id>
   TG_WEBHOOK_SECRET=<random_secret>

   TURNSTILE_SECRET_KEY=<cloudflare_turnstile_key>

   MINIO_ENDPOINT=minio:9000
   MINIO_ACCESS_KEY=minio_admin
   MINIO_SECRET_KEY=<strong_password>
   MINIO_BUCKET_NAME=agroprom-media
   ```

### Запуск и сборка

```bash
# Запустить все сервисы (PostgreSQL, Redis, MinIO, FastAPI + Vue 3 Frontend)
docker compose up -d --build

# Применить миграции БД
docker compose exec app alembic upgrade head
```

### Локальная разработка фронтенда (HMR / Hot Reload)

```bash
cd frontend
npm install
npm run dev
```

---

## 📁 6. Структура проекта

```text
AgroMachines/
├── docker-compose.yml          # Оркестрация сервисов (Postgres, Redis, MinIO, App)
├── Dockerfile                  # Multi-stage сборка: фронтенд (Node 22) + бэкенд (Python 3.12)
├── .dockerignore               # Оптимизация контекста Docker-сборки
├── .gitignore                  # Глобальные правила игнорирования Git
├── .env.example                # Шаблон конфигурации переменных окружения
├── backup.sh                   # Скрипт автоматического бэкапа БД и MinIO
│
├── backend/
│   ├── requirements.txt        # Зависимости Python
│   ├── alembic/                # Миграции БД
│   └── app/
│       ├── main.py             # Точка входа FastAPI (API + раздача SPA)
│       ├── api/v1/             # Роутеры: auth, leads, machines, telegram, audit
│       ├── core/               # Config (Pydantic Settings), Security (JWT, Argon2)
│       ├── db/                 # SQLAlchemy engine, Redis pool
│       ├── models/             # ORM-модели: User, Machine, Lead, AuditLog
│       ├── repositories/       # Слой запросов к БД (Repository Pattern)
│       ├── schemas/            # Pydantic DTO (requests / responses)
│       ├── services/           # Бизнес-логика
│       └── workers/            # Фоновые задачи (отправка в Telegram)
│
└── frontend/                   # Vue 3 / Vite SPA
    ├── src/
    │   ├── views/              # Страницы: каталог, карточка, форма, админка
    │   ├── components/         # UI-компоненты
    │   ├── stores/             # Pinia (auth, catalog, leads)
    │   └── router/             # Vue Router
    └── vite.config.js
```

---

## 🔄 7. Ключевые бизнес-сценарии

### Клиент оставляет заявку
1. Заполняет форму → фронтенд отправляет `POST /api/v1/leads/` с токеном Turnstile
2. Бэкенд: проверяет капчу → валидирует телефон → проверяет дубль в БД → сохраняет заявку
3. **BackgroundTask:** форматирует сообщение и отправляет в Telegram-группу менеджеров с кнопками
4. Клиент получает ответ `200 OK` мгновенно, не ожидая ответа Telegram

### Менеджер обрабатывает заявку
1. Получает сообщение в Telegram с кнопками «Взять в работу» / «Завершить»
2. Нажимает кнопку → Telegram шлёт callback на `POST /api/tg/webhook`
3. Бэкенд атомарно обновляет статус (защита от гонки состояний)
4. Сообщение в Telegram редактируется — отображает «В работе у @username»

### Администратор управляет каталогом
1. Логин через `/admin` → получает Access Token (RAM) + Refresh Token (HttpOnly cookie)
2. CRUD техники с загрузкой фото → фото уходят в MinIO, URL записывается в PostgreSQL
3. Все действия логируются в `audit_logs` с типом действия и ID объекта
4. Суперадмин видит журнал аудита с фильтрами по пользователю, действию, типу объекта

---

## 💾 8. Обслуживание и бэкапы

Скрипт `backup.sh` запускается автоматически (cron) раз в сутки:

- **`pg_dump` + gzip** — дамп PostgreSQL с архивированием
- **Синхронизация MinIO** — резервная копия медиа-бакета
- **Ротация логов аудита** — автоудаление записей старше 90 дней
- **Ротация бэкапов** — хранение последних 30 дней с шифрованием перед отправкой во внешнее хранилище
