# 導入Discord.py模組
# bot.py
import discord
from discord.ext import commands
import asyncio
from goo_crawler import crawl_goo_entries  # 匯入爬蟲函式

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
    await asyncio.sleep(1)  # 避免頻繁請求

    entries = await asyncio.to_thread(crawl_goo_entries, word)
    if not entries:
        await ctx.send(f"找不到『{word}』的資料。")
        return

    # 只取前三個詞條
    entries = entries[:3]

    # Discord 訊息最大長度約2000字，分段發送
    for i, entry in enumerate(entries, 1):
        msg = f"詞條{i}: {entry['title']}\n定義: {entry['definition']}\n"
        try:
            await ctx.send(msg)
        except discord.HTTPException:
            # 若訊息過長，可拆分或簡化內容
            truncated_msg = msg[:1900] + "..."
            await ctx.send(truncated_msg)



bot.run('MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc')
#MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc