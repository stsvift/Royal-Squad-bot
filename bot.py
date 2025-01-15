import discord
from discord.ext import commands
import random
import os
import asyncio
import json
import time
import telebot
import threading
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Файл для хранения очков пользователей
POINTS_FILE = 'user_points.json'

# Файл для хранения ежедневных наград
DAILY_FILE = 'daily_rewards.json'

# Файл для хранения маппинга Discord и Telegram ID
TELEGRAM_ID_MAP_FILE = 'discord_telegram_map.json'

# Функция загрузки очков
def load_points():
    try:
        with open(POINTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Функция сохранения очков
def save_points(points):
    with open(POINTS_FILE, 'w') as f:
        json.dump(points, f, indent=4)

# Функция загрузки маппинга Discord и Telegram ID
def load_telegram_id_map():
    """Загрузка маппинга Discord и Telegram ID"""
    try:
        with open(TELEGRAM_ID_MAP_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Функция сохранения маппинга Discord и Telegram ID
def save_telegram_id_map(telegram_map):
    """Сохранение маппинга Discord и Telegram ID"""
    with open(TELEGRAM_ID_MAP_FILE, 'w') as f:
        json.dump(telegram_map, f, indent=4)

# Токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_IDS = [int(chat_id) for chat_id in os.getenv('TELEGRAM_CHAT_IDS', '').split(',')]
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Создаем телеграм-бота
telegram_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Создаем отдельного бота для Telegram
tg_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Загружаем маппинг при старте
DISCORD_TO_TELEGRAM_MAP = load_telegram_id_map()

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Функция для запуска Telegram бота в отдельном потоке
def start_telegram_bot():
    @tg_bot.message_handler(commands=['discord'])
    def send_to_discord(message):
        # Отправка сообщения из Telegram в Discord
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        
        if message.text.startswith('/discord '):
            text = message.text.replace('/discord ', '')
            asyncio.run_coroutine_threadsafe(
                channel.send(f"📩 Сообщение из Telegram от {message.from_user.username}: {text}"), 
                bot.loop
            )
            tg_bot.reply_to(message, "✅ Сообщение отправлено в Discord")

    @tg_bot.message_handler(commands=['online'])
    def check_discord_online(message):
        # Список ID каналов для отслеживания
        TARGET_CHANNEL_IDS = [int(channel_id) for channel_id in os.getenv('TARGET_VOICE_CHANNEL_IDS', '').split(',')]
        
        # Список онлайн пользователей в указанных каналах
        online_members = []
        for channel_id in TARGET_CHANNEL_IDS:
            channel = bot.get_channel(channel_id)
            if channel:
                channel_members = [member.name for member in channel.members if not member.bot]
                online_members.extend(channel_members)
        
        if online_members:
            response = "👥 Онлайн в указанных каналах:\n" + "\n".join(set(online_members))
        else:
            response = "🕳️ Никого нет онлайн в указанных каналах"
        
        tg_bot.reply_to(message, response)

    # Запуск Telegram бота
    print("Telegram бот запущен")
    tg_bot.polling(none_stop=True)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')
    
    # Запуск Telegram бота в отдельном потоке
    telegram_thread = threading.Thread(target=start_telegram_bot)
    telegram_thread.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == 'casino':
            await ctx.send("❌ Использование: `!casino [количество очков]`\n"
                           "Пример: `!casino 100`\n"
                           "Введите сумму, которую хотите поставить в казино.")
        elif ctx.command.name == 'transfer':
            await ctx.send("❌ Использование: `!transfer @пользователь [количество очков]`\n"
                           "Пример: `!transfer @Username 50`\n"
                           "Укажите пользователя и количество очков для перевода.")
    elif isinstance(error, commands.BadArgument):
        if ctx.command.name == 'casino':
            await ctx.send("❌ Ошибка: количество очков должно быть целым числом.\n"
                           "Пример: `!casino 100`")
        elif ctx.command.name == 'transfer':
            await ctx.send("❌ Ошибка: неверный формат перевода.\n"
                           "Пример: `!transfer @Username 50`")

@bot.event
async def on_voice_state_update(member, before, after):
    # Список ID каналов, за которыми следим
    TARGET_CHANNEL_IDS = [int(channel_id) for channel_id in os.getenv('TARGET_VOICE_CHANNEL_IDS', '').split(',')]
    
    # Проверяем, что пользователь зашел в один из нужных каналов
    if after.channel and after.channel.id in TARGET_CHANNEL_IDS:
        message = f"👋 Пользователь {member.name} зашел в голосовой канал {after.channel.name}!"
        try:
            # Отправляем сообщение во все указанные чаты
            for chat_id in TELEGRAM_CHAT_IDS:
                telegram_bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! Задержка: {round(bot.latency * 1000)}ms')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Привет, {ctx.author.name}!')

@bot.command()
async def profile(ctx):
    points = load_points()
    user_id = str(ctx.author.id)
    user_points = points.get(user_id, 0)
    
    # Определение уровня
    level = user_points // 100 + 1
    
    embed = discord.Embed(title=f"Профиль {ctx.author.name}", color=discord.Color.blue())
    embed.add_field(name="🏆 Очки", value=user_points, inline=False)
    embed.add_field(name="🌟 Уровень", value=level, inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def helpme(ctx):
    help_text = """
🛠 Утилиты:
!settgid [Telegram ID] - привязать Telegram ID
!mytgid - показать свой привязанный Telegram ID
!send [@пользователь] [сообщение] - отправить личное сообщение в Telegram
!tg [сообщение] - отправить сообщение во все чаты
!online - список онлайн пользователей
!profile - посмотреть свой профиль
!top - топ игроков

🎲 Игры:
!daily - ежедневная награда
!casino [ставка] - рискованная игра
!weekly_lottery - еженедельный розыгрыш
!transfer [@пользователь] [количество] - перевод очков
    """
    await ctx.send(help_text)

@bot.command()
async def roll(ctx, sides: int = 6):
    result = random.randint(1, sides)
    await ctx.send(f'🎲 Выпало число: {result}')

@bot.command()
async def top(ctx):
    points = load_points()
    # Сортировка по очкам в убывающем порядке
    sorted_users = sorted(points.items(), key=lambda x: x[1], reverse=True)[:5]
    
    embed = discord.Embed(title="🏆 Топ игроков", color=discord.Color.gold())
    for i, (user_id, user_points) in enumerate(sorted_users, 1):
        try:
            member = await ctx.guild.fetch_member(int(user_id))
            embed.add_field(name=f"{i}. {member.name}", value=f"Очки: {user_points}", inline=False)
        except:
            pass
    
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    points = load_points()
    user_id = str(ctx.author.id)
    
    # Проверка последнего получения награды
    try:
        with open(DAILY_FILE, 'r') as f:
            daily_rewards = json.load(f)
    except FileNotFoundError:
        daily_rewards = {}
    
    last_claim = daily_rewards.get(user_id, 0)
    current_time = int(time.time())
    
    # Проверка, прошло ли 24 часа
    if current_time - last_claim >= 86400:
        daily_reward = random.randint(50, 200)
        points[user_id] = points.get(user_id, 0) + daily_reward
        save_points(points)
        
        # Обновляем время последнего получения награды
        daily_rewards[user_id] = current_time
        with open(DAILY_FILE, 'w') as f:
            json.dump(daily_rewards, f, indent=4)
        
        await ctx.send(f"🎁 Ежедневная награда: {daily_reward} очков!")
    else:
        hours_left = int((86400 - (current_time - last_claim)) / 3600)
        await ctx.send(f"⏰ Следующая награда будет доступна через {hours_left} часов")

@bot.command()
async def casino(ctx, bet: int):
    points = load_points()
    user_id = str(ctx.author.id)
    user_points = points.get(user_id, 0)
    
    if bet <= 0:
        await ctx.send("Ставка должна быть положительной!")
        return
    
    if bet > user_points:
        await ctx.send(f"У вас недостаточно очков. Ваш баланс: {user_points}")
        return
    
    # Шанс выигрыша уменьшен до 20%
    if random.random() < 0.2:
        win_multiplier = random.uniform(2.0, 4.0)  # Увеличен множитель выигрыша
        win_amount = int(bet * win_multiplier)
        points[user_id] += win_amount - bet
        save_points(points)
        await ctx.send(f"🎰 Джекпот! Вы выиграли {win_amount} очков!")
    else:
        points[user_id] -= bet
        save_points(points)
        await ctx.send(f"😢 К сожалению, вы проиграли {bet} очков")

@bot.command()
async def casino_help(ctx):
    help_text = """
🎰 Команда Казино 🎰

Правила игры:
- Введите команду `!casino` с количеством очков для ставки
- Шанс выигрыша: 40%
- Множитель выигрыша: 1.5x - 3.0x
- Можно проиграть или выиграть очки

Примеры:
`!casino 100` - поставить 100 очков
`!casino 500` - поставить 500 очков

⚠️ Осторожно: игра с риском!
    """
    await ctx.send(help_text)

@bot.command()
async def weekly_lottery(ctx):
    points = load_points()
    
    # Случайный победитель
    if not points:
        await ctx.send("Пока нет участников!")
        return
    
    winner_id = random.choice(list(points.keys()))
    winner = await ctx.guild.fetch_member(int(winner_id))
    
    lottery_prize = 500
    points[winner_id] = points.get(winner_id, 0) + lottery_prize
    save_points(points)
    
    await ctx.send(f"🎉 Победитель недельной лотереи: {winner.mention}! Приз: {lottery_prize} очков!")

@bot.command()
async def transfer(ctx, member: discord.Member, amount: int):
    points = load_points()
    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)
    
    if amount <= 0:
        await ctx.send("Сумма перевода должна быть положительной!")
        return
    
    if points.get(sender_id, 0) < amount:
        await ctx.send(f"У вас недостаточно очков. Ваш баланс: {points.get(sender_id, 0)}")
        return
    
    points[sender_id] = points.get(sender_id, 0) - amount
    points[receiver_id] = points.get(receiver_id, 0) + amount
    save_points(points)
    
    await ctx.send(f"💸 Вы перевели {amount} очков пользователю {member.mention}")

@bot.command()
async def transfer_help(ctx):
    help_text = """
💸 Команда Перевода Очков 💸

Правила перевода:
- Используйте `!transfer @пользователь количество_очков`
- Можно перевести очки другому участнику сервера
- Нельзя перевести больше очков, чем у вас есть

Примеры:
`!transfer @Username 50` - перевести 50 очков
`!transfer @Friend 100` - перевести 100 очков

✅ Моментальный перевод без комиссии!
    """
    await ctx.send(help_text)

@bot.command()
async def settgid(ctx, telegram_id: int):
    """Привязать Telegram ID к Discord аккаунту"""
    # Преобразуем ID в строку для JSON сериализации
    discord_id_str = str(ctx.author.id)
    
    # Обновляем словарь
    DISCORD_TO_TELEGRAM_MAP[discord_id_str] = telegram_id
    
    # Сохраняем в файл
    save_telegram_id_map(DISCORD_TO_TELEGRAM_MAP)
    
    await ctx.send(f"✅ Ваш Telegram ID ({telegram_id}) успешно зарегистрирован")

@bot.command()
async def mytgid(ctx):
    """Показать привязанный Telegram ID"""
    discord_id_str = str(ctx.author.id)
    telegram_id = DISCORD_TO_TELEGRAM_MAP.get(discord_id_str)
    
    if telegram_id:
        await ctx.send(f"🆔 Ваш привязанный Telegram ID: {telegram_id}")
    else:
        await ctx.send("❌ У вас не установлен Telegram ID. Используйте !settgid")

@bot.command()
async def send(ctx, member: discord.Member, *, message: str):
    """Отправить личное сообщение пользователю в Telegram"""
    # Преобразуем ID в строку для поиска
    discord_id_str = str(member.id)
    
    # Проверяем, есть ли у пользователя Telegram ID
    telegram_user_id = DISCORD_TO_TELEGRAM_MAP.get(discord_id_str)
    
    if not telegram_user_id:
        await ctx.send(f"❌ Для пользователя {member.name} не указан Telegram ID")
        return
    
    try:
        # Отправляем личное сообщение в Telegram
        telegram_bot.send_message(
            telegram_user_id, 
            f"💬 Личное сообщение от {ctx.author.name} с Discord:\n{message}"
        )
        
        # Подтверждение в Discord
        await ctx.send(f"✅ Сообщение отправлено пользователю {member.name} в Telegram")
    
    except Exception as e:
        await ctx.send(f"❌ Ошибка отправки сообщения: {e}")

# Получаем токен из переменных окружения
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
bot.run(TOKEN)