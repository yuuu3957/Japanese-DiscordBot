import discord
from discord.ext import commands
import asyncio
import getpass
import os
from goo_crawler import crawl_word_full  # 爬蟲函式
from Jishon import lookup_word  # Jisho API
from groq_help import start_groq, generate_japanese_thoughts  # Groq

def set_env(var: str, val: str = None):
    if val is not None:
        os.environ[var] = val
        return val
    if not os.environ.get(var):
        val = getpass.getpass(f"{var}: ")
        os.environ[var] = val
        return val
    else:
        return os.environ.get(var)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
model, client = start_groq()

class LookupView(discord.ui.View):
    def __init__(self, word, jisho_msg, goo_msg, groq_msg):
        super().__init__()
        self.word = word
        self.jisho_msg = jisho_msg
        self.goo_msg = goo_msg
        self.groq_msg = groq_msg

    @discord.ui.button(label="Jisho 查詢", style=discord.ButtonStyle.primary)
    async def jisho_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【Jisho API】查詢結果：\n{self.jisho_msg}", ephemeral=False)

    @discord.ui.button(label="Goo 辞書", style=discord.ButtonStyle.secondary)
    async def goo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【goo 辞書】查詢結果：\n{self.goo_msg}", ephemeral=False)

    @discord.ui.button(label="Groq AI 回答", style=discord.ButtonStyle.success)
    async def groq_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【Groq AI】回答：\n{self.groq_msg}", ephemeral=False)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def lookup(ctx, *, word: str):
    await ctx.send(f"正在查詢「{word}」，請稍候...")
    await asyncio.sleep(1)

    # 非同步執行阻塞的爬蟲函式，爬 goo辞書
    results = await asyncio.to_thread(crawl_word_full, word, 3)

    # 非同步執行 Jisho API 查詢
    jp, en = await asyncio.to_thread(lookup_word, word)

    # 組訊息
    if jp:
        jisho_msg = f"日文：{jp}\n英文解釋：{en}"
    else:
        jisho_msg = "無資料"

    goo_msg = ""
    for i, entry in enumerate(results, 1):
        title = entry['title'] or "無標題"
        definition = entry['definition'] or "無定義"
        goo_msg += f"詞條{i}：{title}\n定義：{definition}\n"

    groq_result = generate_japanese_thoughts(word, model, client)
    groq_msg = groq_result or "無資料"

    view = LookupView(word, jisho_msg, goo_msg, groq_msg)
    await ctx.send("請點選下方按鈕查看不同資料來源的查詢結果", view=view)

bot_key = set_env("DC_Robot_KEY")
bot.run(bot_key)