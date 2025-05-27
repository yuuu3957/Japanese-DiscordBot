import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import getpass
import os
from goo_crawler import crawl_word_full  # 爬蟲函式
from Jishon import lookup_word  # Jisho API
from groq_help import start_groq, generate_japanese_lookup, generate_japanese_addnote # Groq
from add_note import add_or_update_word, load_user_notebook, parse_args_to_dict, add_word_to_notebook
import ButtonClass
import ModalClass


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
channel_id = int(set_env("Channel_ID").strip())


@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"{bot.user} Log in")

    try:
        
        channel = bot.get_channel(channel_id)

        if channel:   
            
            embed = discord.Embed(
                title="📚 歡迎使用日文小助手！",
                description=(
                    "**功能說明：**\n\n"
                    "🔍 **查詢功能**\n"
                    "  輸入 `!lookup <日文字>` 即可查詢該單字的詳細解釋與例句。\n\n"
                    "📝 **學習本功能**\n"
                    "  使用 `!addword <單字> <中文解釋>` 將單字加入你的學習本。\n\n"
                    "  使用 `!mynote` 將學習本內容輸出。\n\n"
                    "🧪 **測驗功能**\n"
                    "  輸入 `!quiz` 開始隨機小測驗，幫助複習。\n\n"
                ),
                color=0x57A2DE
            )

            await channel.send(embed=embed)
        
        else :
            print("Can't find Chanel")

    except Exception as e:
        print(f"發送訊息失敗: {e}")

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

    groq_result = generate_japanese_lookup(word, model, client)
    groq_msg = groq_result or "無資料"

    view = ButtonClass.LookupView(word, jisho_msg, goo_msg, groq_msg)
    await ctx.send(
        "🔎 **查詢完畢！**\n"
        "請點選下方按鈕查看不同資料來源的查詢結果。",
        view=view
    )

@bot.command()
async def mynote(ctx):
    user_id = str(ctx.author.id)
    notebook = load_user_notebook(user_id)
    if not notebook:
        await ctx.send("你的學習本目前是空的喔！")
        return

    view = ButtonClass.NotebookView(notebook, ctx.author.id)
    embed = view.get_page_embed()
    await ctx.send(embed=embed, view=view)

@app_commands.command(name="addnote", description="新增詞彙到學習本")
async def addnote(interaction: discord.Interaction):
    modal = ModalClass.AddNoteModal()
    await interaction.response.send_modal(modal)



bot.tree.add_command(addnote)
bot_key = set_env("DC_Robot_KEY")
bot.run(bot_key)