import discord
import ModalClass
import NoteBook
import groq_help
import EditNoteBook
import quiz

Notebook_Page_Size = 3
model, client = groq_help.start_groq()


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
        word_data = groq_help.generate_japanese_addnote(self.groq_msg, model, client)
        word_data["status"] = "未學"
        jp_to_ch = {"correct": 0, "wrong": 0}
        ch_to_jp = {"correct": 0, "wrong": 0}
        word_data["quiz_result"] = {"jp_to_ch" : jp_to_ch, "ch_to_jp" : ch_to_jp}
        word_data["notes"] = ""
        is_new = NoteBook.add_word_to_notebook(user_id, word_data)
        if is_new:
            await interaction.response.send_message(f"✅ 已新增「{self.word}」並加入筆記。")
        else:
            await interaction.response.send_message(f"✏️ 已更新「{self.word}」的筆記。")

class ShowView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.notebook = NoteBook.load_user_notebook(user_id)
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
            if word["status"] == "未學":
                status = "🔴"
            else :
                status = "🟢"

            value = f"中文解釋：{word.get('chinese', '')}\n狀態: {status}\n"
            examples = word.get('examples', [])
            for i, ex in enumerate(examples[:2], 1):
                jp_sentence = ex.get('jp_sentence', '')
                jp_reading = ex.get('jp_reading', '')
                chinese_translation = ex.get('chinese_translation', '')

                if jp_sentence:
                    value += f"例句{i}：{jp_sentence}"
                    if jp_reading:
                        value += f" ({jp_reading})"
                    value += "\n"
                else:
                    # 如果 jp_sentence 是空字串，就只輸出空行或略過
                    continue

                value += f"翻譯{i}：{chinese_translation}\n"
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
                    "  點擊 `Edit` 修改內容\n\n"
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

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        notebook = NoteBook.load_user_notebook(self.user_id)
        paged_view = EditNoteBook.PagedView(notebook)
        await interaction.response.send_message(
            "請從下拉選單選擇要編輯的詞彙：",
            view=paged_view,
            ephemeral=True
        )

class QuizView(discord.ui.View):
    def __init__(self,user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    def get_embed(self):
        embed = discord.Embed(
            title=f"📝 **測驗功能**",
            description=(
                    "請選擇``日譯中`或`中譯日`\n\n"
                ),
            color=0x686FFC
        )
        return embed

    @discord.ui.button(label="日譯中", style=discord.ButtonStyle.success)
    async def jp_to_ch_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = quiz.QuizCountModal("日譯中")
            await interaction.response.send_modal(modal)

    @discord.ui.button(label="中譯日", style=discord.ButtonStyle.danger)
    async def ch_to_jp_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = quiz.QuizCountModal("中譯日")
            await interaction.response.send_modal(modal)


