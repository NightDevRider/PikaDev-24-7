import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os  # Добавляем импорт модуля os
import discord.opus

load_dotenv()
DISCORD_API_KEY = os.getenv('DISCORD_API_KEY')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!!', intents=intents)

if not discord.opus.is_loaded():
    print("Opus не загружен.")
    # Попробуйте указать путь к opus.dll вручную, если нужно
    # discord.opus.load_opus('путь/к/opus.dll')
else:
    print("Opus успешно загружен.")
    
@bot.event
async def on_ready():
    print(f'Залогинен как {bot.user.name}')

@bot.command()
async def play(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("Вы должны быть в голосовом канале, чтобы использовать эту команду.")

    channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected():
        await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()

    def after_playing(error):
        if error:
            print(f"Ошибка воспроизведения: {error}")
        else:
            asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

    async def play_next(ctx):
        with open("link.txt", "r") as f:  
            link = f.read().strip()
        source = discord.FFmpegPCMAudio(link)  
        voice_client.play(source, after=after_playing)

    await play_next(ctx)

@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        voice_client.stop()
        await voice_client.disconnect()
        await ctx.send("Музыка остановлена, бот покинул канал.")
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")

bot.run(DISCORD_API_KEY)
