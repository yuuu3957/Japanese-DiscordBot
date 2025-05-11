# 導入Discord.py模組
# bot.py
import discord
from discord.ext import commands
from dictionary import lookup_word  # 匯入查詢函式

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def lookup(ctx, *, word: str):
    jp_word, meanings = lookup_word(word)
    if jp_word is None:
        await ctx.send(f"找不到『{word}』的資料。")
    else:
        await ctx.send(f"**{jp_word}**: {meanings}")

bot.run('MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc')
#MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc