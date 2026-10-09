# 🤖 Discord Voice Bot

простой и легковесный бот для дискорда, который удерживает постоянное подключение (24/7) к заданному голосовому каналу.

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/kitavix/discord-voicebot.git
cd discord-voicebot
```

### 2. Установка зависимостей
> убедитесь, что у вас установлен Python версии 3.10+ и FFmpeg.
```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
создайте файл `.env` в корневой папке проекта и заполните данные:
```env
DISCORD_TOKEN=ваш_токен_бота
GUILD_ID=айди_сервера
CHANNEL_ID=айди_гч
STATUS_TEXT=статус_бота
BOT_STATUS=сетевой_статус_бота (выберите что-то из этого: online, idle, dnd, invisible)
```

### 4. Запуск
```bash
python main.py
```

---

## 🛠 Стек технологий

* [discord.py](https://github.com/Rapptz/discord.py) — взаимодействие с апи дискорда
* [python-dotenv](https://github.com/theskumar/python-dotenv) — работа с файлом окружения `.env`
