import discord
import ModalClass
import notebook
import groq_help


Notebook_Page_Size = 5
model, client = groq_help.start_groq()


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
        word_data = groq_help.generate_japanese_addnote(self.groq_msg, model, client)
        print (word_data)
        word_data["japanese"] = self.word
        word_data["status"] = "未學"
        note = ""
        is_new = notebook.add_or_update_word(user_id, word_data, note)
        if is_new:
            await interaction.response.send_message(f"✅ 已新增「{self.word}」並加入筆記。")
        else:
            await interaction.response.send_message(f"✏️ 已更新「{self.word}」的筆記。")

class ShowView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.notebook = notebook.load_user_notebook(user_id)
        self.user_id = user_id
        self.cur_page = 0
        self.max_page = (len(self.notebook) - 1)  // Notebook_Page_Size

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
        if int(interaction.user.id) != int(self.user_id):
            await interaction.response.send_message("這不是你的學習本喔！", ephemeral=True)
            return
        if self.cur_page > 0:
            self.cur_page -= 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.send_message("已經是第一頁了。", ephemeral=True)

    @discord.ui.button(label="下一頁", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if int(interaction.user.id) != int(self.user_id):
            await interaction.response.send_message("這不是你的學習本喔！", ephemeral=True)
            return
        if self.cur_page < self.max_page:
            self.cur_page += 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.send_message("已經是最後一頁了。", ephemeral=True)

class NotebookView(discord.ui.View):
    def __init__(self,user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    def get_embed(self):
        embed = discord.Embed(
            title=f"📝 **學習本功能**",
            description=(
                    "**功能說明：**\n\n"
                    "  點擊 `Add` 添加筆記至學習本\n\n"
                    "  點擊 `Delete` 刪除單字。\n\n"
                    "  點擊 `Show` 將學習本內容輸出。\n\n"
                    "  點擊 `Update` 修改內容\n\n"
                ),
            color=0x686FFC
        )
        return embed

    @discord.ui.button(label="Add", style=discord.ButtonStyle.success)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ModalClass.AddNoteModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ModalClass.DeleteNoteModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Show", style=discord.ButtonStyle.primary)
    async def show_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        show_view = ShowView(self.user_id)
        show_embed = show_view.get_page_embed()

        await interaction.response.send_message(
            embed=show_embed,
            view=show_view,
            ephemeral=True
        )

    @discord.ui.button(label="Update", style=discord.ButtonStyle.secondary)
    async def update_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("你點了 Update 按鈕", ephemeral=True)

