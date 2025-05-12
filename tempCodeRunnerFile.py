# 導入Discord.py模組
# bot.py
import discord
from discord.ext import commands
import asyncio
from goo_crawler import crawl_goo_dictionary

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!我是你的日文小助手!')

@bot.command()
async def lookup(ctx, *, word: str):
    await ctx.send(f"正在查詢『{word}』，請稍候...")
    await asyncio.sleep(1)  # 避免過度頻繁請求

    result = await asyncio.to_thread(crawl_goo_dictionary, word)
    if result:
        if len(result) > 1900:
            result = result[:1900] + "..."
        await ctx.send(f"『{word}』的解釋：\n{result}")
    else:
        await ctx.send(f"抱歉，找不到『{word}』的解釋。")

bot.run('MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc')
#MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc