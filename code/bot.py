import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import asyncio
import getpass
import os
from groq_help import start_groq
from lookup_code.goo_crawler import crawl_word_full  # 爬蟲函式
from lookup_code.Jisho import lookup_word  # Jisho API
from lookup_code.lookup_groq import generate_japanese_lookup
from lookup_code.lookup_base import lookup_word_full
from lookup_code.ui.lookup_base_ui import LookupView
from notebook_code.ui.notebook_base_ui import NotebookView
from quiz_code.ui.quiz_base_ui import QuizView


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
                    "🎯 **測驗功能**\n"
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

    jisho_result, goo_result, groq_result = await lookup_word_full(word, model, client)

    lookup_view = LookupView(word, jisho_result, goo_result, groq_result)
    await ctx.send(
        embed = lookup_view.get_embed(),
        view=lookup_view
    )

@bot.command()
async def notebook(ctx):
    user_id = str(ctx.author.id)
    view = NotebookView(user_id)
    embed = view.get_embed()
    await ctx.send(embed=embed,view=view)
    

@bot.command()
async def quiz(ctx):
    user_id = str(ctx.author.id)
    view = QuizView(user_id)
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