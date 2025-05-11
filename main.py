# 導入Discord.py模組
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # 允許讀取訊息內容

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

bot.run('MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc')