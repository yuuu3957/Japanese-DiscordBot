import discord
from discord.ext import commands
import asyncio
import add_note

Notebook_Page_Size = 5


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

    @discord.ui.button(label="Goo 辞書", style=discord.ButtonStyle.primary)
    async def goo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【goo 辞書】查詢結果：\n{self.goo_msg}", ephemeral=False)

    @discord.ui.button(label="Groq AI 回答", style=discord.ButtonStyle.primary)
    async def groq_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"【Groq AI】回答：\n{self.groq_msg}", ephemeral=False)
    
    @discord.ui.button(label="加入學習本", style=discord.ButtonStyle.primary)
    async def add_note_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        word_data = add_note.generate_japanese_addnote(self.groq_msg, model, client)
        print (word_data)
        word_data["japanese"] = self.word
        word_data["status"] = "未學"
        note = ""
        is_new = add_note.add_or_update_word(user_id, word_data, note)
        if is_new:
            await interaction.response.send_message(f"✅ 已新增「{self.word}」並加入筆記。")
        else:
            await interaction.response.send_message(f"✏️ 已更新「{self.word}」的筆記。")

class NotebookView(discord.ui.View):
    def __init__(self, notebook, user_id):
        super().__init__(timeout=120)
        self.notebook = notebook
        self.user_id = user_id
        self.cur_page = 0
        self.max_page = (len(notebook) - 1)  // Notebook_Page_Size

    def get_page_embed(self):
        start = self.cur_page * Notebook_Page_Size
        end = start + Notebook_Page_Size
        embed = discord.Embed(
            title=f"你的學習本 - 頁 {self.cur_page + 1} / {self.max_page + 1}",
            color=0x686FFC
        )
        for idx, word in enumerate(self.notebook[start:end], start=1+start):
            name = f"{idx}. {word['japanese']} ({word.get('reading', '')})"
            value = f"中文解釋：{word.get('chinese', '')}\n狀態：{word.get('status', '')}\n"
            examples = word.get('examples', [])
            for i, ex in enumerate(examples[:2], 1):
                value += f"例句{i}：{ex.get('jp_sentence', '')}\n翻譯{i}：{ex.get('chinese_translation', '')}\n"
            embed.add_field(name=name, value=value, inline=False)
        return embed
    
    @discord.ui.button(label="上一頁", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("這不是你的學習本喔！", ephemeral=True)
            return
        if self.cur_page > 0:
            self.cur_page -= 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.send_message("已經是第一頁了。", ephemeral=True)

    @discord.ui.button(label="下一頁", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("這不是你的學習本喔！", ephemeral=True)
            return
        if self.cur_page < self.max_page:
            self.cur_page += 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.send_message("已經是最後一頁了。", ephemeral=True)
