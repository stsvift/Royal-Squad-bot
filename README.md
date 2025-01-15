# 🤖 Discord-Telegram Интеграционный Бот

## 📋 Оглавление
- [Возможности](#-возможности)
- [Установка](#-установка)
- [Настройка](#-настройка)
- [Команды](#-команды)
- [Получение Telegram ID](#-получение-telegram-id)
- [Безопасность](#-безопасность)

## 🌟 Возможности

### Коммуникация
- Двусторонняя интеграция между Discord и Telegram
- Отправка личных и групповых сообщений
- Уведомления о входе в голосовые каналы

### Игровая система
- Казино
- Еженедельная лотерея
- Система очков
- Ежедневные награды
- Перевод очков между пользователями

## 🚀 Установка

### Требования
- Python 3.8+
- discord.py
- pyTelegramBotAPI
- python-dotenv

### Шаги установки
1. Клонируйте репозиторий
   ```bash
   git clone https://github.com/ваш_репозиторий/discordbot.git
   cd discordbot
   ```

2. Создайте виртуальное окружение
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Для Unix/macOS
   # или
   venv\Scripts\activate  # Для Windows
   ```

3. Установите зависимости
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте `.env` файл

## 🔧 Настройка

### Переменные окружения
Создайте файл `.env` с следующими параметрами:

```
DISCORD_BOT_TOKEN=ваш_discord_токен
TELEGRAM_BOT_TOKEN=ваш_telegram_токен
TELEGRAM_CHAT_IDS=список_chat_id
TARGET_VOICE_CHANNEL_IDS=список_голосовых_каналов
DISCORD_CHANNEL_ID=id_канала_discord
```

## 📜 Команды

### 🎮 Команды Discord
#### Утилиты
- `!settgid [Telegram ID]` - Привязать Telegram ID
- `!mytgid` - Показать привязанный Telegram ID
- `!send [@пользователь] [сообщение]` - Личное сообщение в Telegram
- `!profile` - Профиль пользователя
- `!top` - Топ игроков

#### Игры
- `!daily` - Ежедневная награда
- `!casino [ставка]` - Рискованная игра
- `!weekly_lottery` - Еженедельный розыгрыш
- `!transfer [@пользователь] [количество]` - Перевод очков

### � Команды Telegram
#### Утилиты
- `/discord [сообщение]` - Отправить сообщение в Discord
- `/online` - Список онлайн пользователей
- `/start` - Начать взаимодействие с ботом

## 🆔 Как получить Telegram ID

### Метод 1: @userinfobot
1. Откройте Telegram
2. Найдите бота [@userinfobot](https://t.me/userinfobot)
3. Начните чат с ботом
4. Бот автоматически пришлет ваш Telegram ID

### Метод 2: @IDBot
1. Найдите бота [@IDBot](https://t.me/IDBot)
2. Начните чат
3. Отправьте любое сообщение
4. Бот ответит с вашим ID

### Метод 3: Через настройки Telegram
1. Установите приложение Telegram Desktop
2. Перейдите в настройки
3. Нажмите "Расширенные"
4. Включите "Режим разработчика"
5. В профиле появится числовой ID

### Привязка Telegram ID к Discord
1. Получите ID одним из описанных методов
2. В Discord введите: `!settgid ВАШНОМЕР`
3. Проверьте командой `!mytgid`

## �🔒 Безопасность
- Храните токены в `.env`
- Не публикуйте конфиденциальные данные
- Используйте надежные пароли
- Регулярно обновляйте зависимости
- Не передавайте ID посторонним

## 🤝 Вклад в проект
1. Форкните репозиторий
2. Создайте ветку (`git checkout -b feature/новая_функция`)
3. Закоммитьте изменения (`git commit -m 'Добавлена новая функция'`)
4. Запушьте в ветку (`git push origin feature/новая_функция`)
5. Создайте Pull Request

## 📞 Поддержка
По вопросам: [ваш_email@example.com]

## 📄 Лицензия
[Укажите вашу лицензию]

---
*Создано с ❤️ для Discord и Telegram сообществ*