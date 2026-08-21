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
BOT_STATUS_RAW = os.getenv('BOT_STATUS',).lower()
STATUS_MAP = {
    'online': discord.Status.online,
    'idle': discord.Status.idle,
    'dnd': discord.Status.dnd,
    'invisible': discord.Status.invisible
}
BOT_STATUS = STATUS_MAP.get(BOT_STATUS_RAW)

SOUNDS_DIR = './sounds'

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

class VoiceBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(console_listener())
        self.loop.create_task(keep_alive_voice())

bot = VoiceBot(command_prefix="!", intents=intents)
voice_client = None
voice_lock = asyncio.Lock()

# остановка звуков через консоль
def stop_sound():
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        print("[Звук] Воспроизведение остановлено.")
        return True
    else:
        print("[Инфо] Сейчас ничего не воспроизводится.")
        return False

# воспроизведение звуков через консоль
async def play_sound_file(filename):
    global voice_client
    if not voice_client or not voice_client.is_connected():
        print("[Ошибка] Бот не подключен к голосовому каналу!")
        return False

    if not filename.endswith(('.mp3', '.wav', '.ogg')):
        filename += '.mp3'

    sound_path = os.path.join(SOUNDS_DIR, filename)

    if not os.path.exists(sound_path):
        print(f"[Ошибка] Файл '{filename}' не найден в папке {SOUNDS_DIR}!")
        return False

    if voice_client.is_playing():
        voice_client.stop()
        await asyncio.sleep(0.2)

    print(f"[Звук] Играет файл: {filename}")
    audio_source = discord.FFmpegPCMAudio(sound_path)
    voice_client.play(audio_source)
    return True

# консольное управление звуками
async def console_listener():
    await bot.wait_until_ready()
    print("\n==================================================")
    print(" Консольное управление звуками:")
    print(" • 'list' — список всех звуков")
    print(" • 'stop' (или 's') — остановить текущий звук")
    print(" • 'имя_файла' (напр. troll) — воспроизвести файл")
    print("==================================================\n")

    loop = asyncio.get_event_loop()
    while not bot.is_closed():
        cmd = await loop.run_in_executor(None, input)
        cmd = cmd.strip()

        if not cmd:
            continue

        if cmd.lower() in ['stop', 's', 'стоп']:
            stop_sound()

        elif cmd.lower() == 'list':
            if os.path.exists(SOUNDS_DIR):
                sounds = [f for f in os.listdir(SOUNDS_DIR) if f.endswith(('.mp3', '.wav', '.ogg'))]
                print(f"[Доступные файлы ({len(sounds)})]: {', '.join(sounds)}")
            else:
                print(f"[Ошибка] Папка {SOUNDS_DIR} не найдена.")
        else:
            clean_cmd = cmd.replace('play ', '').strip()
            await play_sound_file(clean_cmd)

# удержание бота в войсе
async def join_channel():
    global voice_client
    async with voice_lock:
        if voice_client and voice_client.is_connected():
            return

        guild = bot.get_guild(GUILD_ID)
        if not guild:
            return
        channel = guild.get_channel(CHANNEL_ID)
        if not channel:
            return

        if voice_client:
            try:
                await voice_client.disconnect(force=True)
            except Exception:
                pass
            voice_client = None
            await asyncio.sleep(1.5)

        try:
            voice_client = await channel.connect(reconnect=True, self_deaf=True, timeout=15.0)
            print("--- [Discord] Успешное подключение к голосовому каналу! ---")
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

async def main():
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())