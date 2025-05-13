import discord
from discord.ext import commands
import asyncio
from goo_crawler import crawl_word_full # 匯入爬蟲函式
from Jishon import lookup_word

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def lookup(ctx, *, word: str):
    await ctx.send(f"正在查詢「{word}」，請稍候...")
    await asyncio.sleep(1)  # 控制節奏避免頻繁請求
    msg_jisho=""
    msg_goo=""

    # 非同步執行阻塞的爬蟲函式，爬 goo辞書
    results = await asyncio.to_thread(crawl_word_full, word, 3)  # 只抓前三筆

    # 非同步執行 Jisho API 查詢
    jp, en= await asyncio.to_thread(lookup_word, word)

    if not results and jp is None:
        await ctx.send(f"找不到「{word}」的資料。")
        return

    # 回覆 Jisho API 查詢結果
    if jp:
        msg_jisho = f"【Jisho API】日文：{jp}\n英文解釋：{en}\n"
        #await ctx.send(msg_jisho+"\n")


    # 回覆 goo 辞書爬蟲結果
    for i, entry in enumerate(results, 1):
        title = entry['title'] if entry['title'] else "無標題"
        definition = entry['definition'] if entry['definition'] else "無定義"
        msg_goo += f"【goo 辞書】詞條{i}：{title}\n定義：{definition}\n\n"
        #try:
            #await ctx.send(msg_goo+"\n")
        #except discord.HTTPException:
            #3await ctx.send(msg_goo[:1900] + "..."+"\n")
    
    await ctx.send(msg_jisho+"\n"+msg_goo)


bot.run('MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc')
#MTMwNzY4MDc5OTgyNjUwOTg3NQ.GhyENQ.hyjaWfwa4eBB2e1R5H4Qr-WgSpBuGkhhtMYksc