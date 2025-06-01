import discord
from notebook_code.notebook_groq import generate_japanese_addnote
from notebook_code.notebook_base import add_word_to_notebook
from groq_help import start_groq

model, client = start_groq()


class LookupView(discord.ui.View):
    def __init__(self, word, jisho_msg, goo_msg, groq_msg):
        super().__init__()
        self.word = word
        self.jisho_msg = jisho_msg
        self.goo_msg = goo_msg
        self.groq_msg = groq_msg

    def get_embed(self):
        embed = discord.Embed(
            title=f"🔎 **查詢完畢！**",
            description=(
                    "**功能說明：**\n\n"
                    "  點擊 `Jisho 查詢` 獲得日英對照\n\n"
                    "  點擊 `Goo 辞書` 獲得日日字典查詢結果。\n\n"
                    "  點擊 `Groq AI 回答` 獲得AI回應(含中文和例句)。\n\n"
                    "  點擊 `加入學習本` 將GroqAI回答加入學習本\n\n"
                ),
            color=0x686FFC
        )
        return embed

    @discord.ui.button(label="Jisho 查詢", style=discord.ButtonStyle.primary)
    async def jisho_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【Jisho API】查詢結果：\n{self.jisho_msg}", ephemeral=True)

    @discord.ui.button(label="Goo 辞書", style=discord.ButtonStyle.primary)
    async def goo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【goo 辞書】查詢結果：\n{self.goo_msg}", ephemeral=True)

    @discord.ui.button(label="Groq AI 回答", style=discord.ButtonStyle.primary)
    async def groq_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【Groq AI】回答：\n{self.groq_msg}", ephemeral=True)
    
    @discord.ui.button(label="加入學習本", style=discord.ButtonStyle.primary)
    async def add_note_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        word_data = generate_japanese_addnote(self.groq_msg, model, client)
        word_data["status"] = "未學"
        jp_to_ch = {"correct": 0, "wrong": 0}
        ch_to_jp = {"correct": 0, "wrong": 0}
        word_data["quiz_result"] = {"jp_to_ch" : jp_to_ch, "ch_to_jp" : ch_to_jp}
        word_data["notes"] = ""
        is_new = add_word_to_notebook(user_id, word_data)
        if is_new:
            await interaction.response.send_message(f"✅ 已新增「{self.word}」並加入筆記。")
        else:
            await interaction.response.send_message(f"⚠️ 詞彙「{self.word}」已存在學習本中。")

            