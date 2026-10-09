import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
STATUS_TEXT = os.getenv('STATUS_TEXT')

# настройка сетевого статуса (online, idle, dnd, invisible)
BOT_STATUS_RAW = (os.getenv('BOT_STATUS') or 'dnd').lower()
STATUS_MAP = {
    'online': discord.Status.online,
    'idle': discord.Status.idle,
    'dnd': discord.Status.dnd,
    'invisible': discord.Status.invisible
}
BOT_STATUS = STATUS_MAP.get(BOT_STATUS_RAW, discord.Status.dnd)

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
voice_client = None

async def join_channel():
    global voice_client
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    channel = guild.get_channel(CHANNEL_ID)
    if not channel:
        return

    try:
        if voice_client:
            try:
                await voice_client.disconnect(force=True)
            except Exception:
                pass
        voice_client = await channel.connect(reconnect=True, self_deaf=True, timeout=15.0)
        print(f"--- [Discord] Успешное подключение к каналу '{channel.name}'! ---")
    except Exception as e:
        print(f"[Ошибка войса]: {e}")

async def keep_alive_voice():
    await bot.wait_until_ready()
    while not bot.is_closed():
        if not voice_client or not voice_client.is_connected():
            print("[Войс-контроллер] Обнаружено отключение. Подключаюсь обратно...")
            await join_channel()
        await asyncio.sleep(15)

@bot.event
async def on_voice_state_update(member, before, after):
    global voice_client
    if member.id == bot.user.id:
        if before.channel is not None and after.channel is None:
            print("[Discord] Бот был отключен от канала. Мгновенный перезаход...")
            await asyncio.sleep(2)
            await join_channel()

@bot.event
async def on_ready():
    print(f"Бот запущен под именем {bot.user}")
    activity = discord.Game(name=STATUS_TEXT) if STATUS_TEXT else None
    await bot.change_presence(status=BOT_STATUS, activity=activity)
    await join_channel()
    bot.loop.create_task(keep_alive_voice())

async def main():
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())