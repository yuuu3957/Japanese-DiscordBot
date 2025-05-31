import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord import app_commands
import asyncio
import getpass
import os
from goo_crawler import crawl_word_full  # 爬蟲函式
from Jishon import lookup_word  # Jisho API
from groq_help import start_groq, generate_japanese_lookup, generate_japanese_addnote # Groq
from NoteBook import add_or_update_word, load_user_notebook, parse_args_to_dict, add_word_to_notebook
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
                    "  使用 `!notebook` 可使用學習本功能。\n\n"
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

    lookup_view = ButtonClass.LookupView(word, jisho_msg, goo_msg, groq_msg)
    await ctx.send(
        "🔎 **查詢完畢！**\n",
        embed = lookup_view.get_embed(),
        view=lookup_view
    )

@bot.command()
async def notebook(ctx):
    user_id = str(ctx.author.id)
    view = ButtonClass.NotebookView(user_id)
    embed = view.get_embed()
    await ctx.send(embed=embed,view=view)
    

@bot.command()
async def quiz(ctx):
    user_id = str(ctx.author.id)
    view = ButtonClass.QuizView(user_id)
    embed = view.get_embed()
    await ctx.send(embed=embed,view=view)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send(f"抱歉，指令 `{ctx.invoked_with}` 不存在，請確認指令是否正確。")
    else:
        # 其他錯誤可用這裡處理或直接 raise
        raise error


bot_key = set_env("DC_Robot_KEY")
bot.run(bot_key)