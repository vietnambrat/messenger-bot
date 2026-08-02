# messenger-bot

Бот с автоответами для Telegram и Facebook Messenger / Instagram.
Логика ответов — простые правила по ключевым словам, см. `config/replies.py`.
В продакшене (Render) оба канала работают через webhook — процесс не должен
постоянно опрашивать API, что подходит для бесплатного плана Render.

## Локальный запуск (для разработки)

```bash
cd ~/messenger-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`. Для локального теста Telegram без публичного HTTPS поставьте
`TELEGRAM_USE_POLLING=1` — бот будет опрашивать Telegram сам, вебхук не нужен.

```bash
python3 app.py
```

## Настройка Telegram

1. В Telegram напишите `@BotFather` → `/newbot`, следуйте инструкциям.
2. Скопируйте токен в `.env` → `TELEGRAM_BOT_TOKEN`.
3. Придумайте случайную строку → `.env` → `TELEGRAM_WEBHOOK_SECRET`
   (защищает `/webhook/telegram` от посторонних запросов).
4. После деплоя (см. ниже) зарегистрируйте webhook одной командой.

## Настройка Facebook Messenger + Instagram

Оба канала используют один Meta Graph API и один webhook (`/webhook/meta`).

1. Создайте приложение на https://developers.facebook.com/apps (тип "Business").
2. Добавьте продукт **Messenger**, привяжите Facebook-страницу, сгенерируйте
   Page Access Token → `.env` → `META_PAGE_ACCESS_TOKEN`.
3. Для Instagram: аккаунт должен быть Business/Creator и привязан к той же
   странице. Добавьте продукт **Instagram**.
4. Придумайте случайную строку → `.env` → `META_VERIFY_TOKEN`.
5. В "App settings → Basic" скопируйте **App Secret** → `.env` → `META_APP_SECRET`.
6. После деплоя в настройках Messenger/Instagram webhook укажите:
   - Callback URL: `https://ваш-сервис.onrender.com/webhook/meta`
   - Verify Token: значение `META_VERIFY_TOKEN`
   - Подпишитесь на поле `messages`.
7. Пока приложение не прошло App Review, оно работает только с аккаунтами,
   добавленными в разделе "Roles → Testers" вашего приложения.

## Деплой на Render

Репозиторий уже содержит `render.yaml` — Render подхватит настройки
автоматически (Blueprint).

1. Создайте git-репозиторий и запушьте код на GitHub:
   ```bash
   cd ~/messenger-bot
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <URL вашего репозитория на GitHub>
   git push -u origin main
   ```
2. На https://dashboard.render.com → **New → Blueprint** → выберите репозиторий.
   Render прочитает `render.yaml` и создаст веб-сервис на бесплатном плане.
3. В настройках сервиса на Render (Environment) заполните переменные:
   `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `META_VERIFY_TOKEN`,
   `META_PAGE_ACCESS_TOKEN`, `META_APP_SECRET`.
4. Дождитесь деплоя, скопируйте публичный URL сервиса
   (вида `https://messenger-bot-xxxx.onrender.com`).
5. Зарегистрируйте Telegram webhook на этот URL:
   ```bash
   TELEGRAM_BOT_TOKEN=xxx TELEGRAM_WEBHOOK_SECRET=xxx \
     python3 scripts/set_telegram_webhook.py https://messenger-bot-xxxx.onrender.com
   ```
6. Укажите тот же URL + `/webhook/meta` в настройках Meta-приложения (шаг 6
   раздела выше).

**Важно про бесплатный план Render:** сервис засыпает после ~15 минут
без запросов и просыпается несколько секунд при следующем сообщении —
это нормально для автоответов, просто первый ответ после паузы придёт
с небольшой задержкой.

## Как менять ответы

Правила лежат в `config/replies.py` — список пар `(ключевые слова, ответ)`
плюс `DEFAULT_REPLY` на случай, если ни одно правило не подошло. Изменения
вступают в силу после нового деплоя (`git push`, Render передеплоит сам).
