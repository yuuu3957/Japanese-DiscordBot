import discord
from ..notebook_edit import edit_word

PAGE_SIZE = 25

# 分頁下拉選單
class PagedWordSelect(discord.ui.Select):
    def __init__(self, words, page=0):
        self.words = words
        self.page = page
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        options = [
            discord.SelectOption(label=w["japanese"], description=w.get("chinese", ""), value=w["japanese"])
            for w in words[start:end]
        ]
        super().__init__(placeholder=f"選擇詞彙 (第 {page+1} 頁)", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_word = self.values[0]
        await interaction.response.send_message(f"你選擇了「{selected_word}」，請選擇要修改的欄位。", view=FieldSelectView(selected_word), ephemeral=True)

# 分頁按鈕 + 下拉選單
class PagedView(discord.ui.View):
    def __init__(self, words):
        super().__init__(timeout=120)
        self.words = words
        self.page = 0
        self.max_page = (len(words) - 1) // PAGE_SIZE

        self.select = PagedWordSelect(words, self.page)
        self.add_item(self.select)

        self.prev_button = discord.ui.Button(label="上一頁", style=discord.ButtonStyle.secondary)
        self.next_button = discord.ui.Button(label="下一頁", style=discord.ButtonStyle.secondary)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

        self.update_button_state()

    def update_button_state(self):
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page == self.max_page

    async def prev_page(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            self.select.page = self.page
            self.select.options = self.generate_options()
            self.update_button_state()
            await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.page < self.max_page:
            self.page += 1
            self.select.page = self.page
            self.select.options = self.generate_options()
            self.update_button_state()
            await interaction.response.edit_message(view=self)

    def generate_options(self):
        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE
        return [
            discord.SelectOption(label=w["japanese"], description=w.get("chinese", ""), value=w["japanese"])
            for w in self.words[start:end]
        ]
    
class FieldSelectView(discord.ui.View):
    def __init__(self, word):
        super().__init__()
        self.add_item(FieldSelect(word))

class FieldSelect(discord.ui.Select):
    def __init__(self, word):
        self.word = word
        options = [
            discord.SelectOption(label="日文", value="japanese"),
            discord.SelectOption(label="中文解釋", value="chinese"),
            discord.SelectOption(label="讀音", value="reading"),
            discord.SelectOption(label="例句1-日文", value="example1 jp_sentence"),
            discord.SelectOption(label="例句1-中文", value="example1 chinese_translation"),
            discord.SelectOption(label="例句1-假名", value="example1 jp_reading"),
            discord.SelectOption(label="例句2-日文", value="example2 jp_sentence"),
            discord.SelectOption(label="例句2-假名", value="example2 jp_reading"),
            discord.SelectOption(label="筆記", value="note"),
            discord.SelectOption(label="狀態(僅可改為未學)", value="status")
        ]

        super().__init__(placeholder="選擇要修改的欄位", options=options)

    async def callback(self, interaction: discord.Interaction):
        
        field = self.values[0]
        modal = EditModal(self.word, field)
        await interaction.response.send_modal(modal)


class EditModal(discord.ui.Modal):
    def __init__(self, word, field):
        super().__init__(title=f"修改「{word}」的 {field} 資料")
        self.word = word
        self.field = field
        self.new_value = discord.ui.TextInput(label=f"請輸入新的 {field}：", style=discord.TextStyle.paragraph)
        self.add_item(self.new_value)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        modified = edit_word(user_id, self.word, self.field, self.new_value.value)

        if modified:
            await interaction.response.send_message(
                f"✅ 已成功將「{self.word}」的 {self.field} 更新為：{self.new_value.value}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ 找不到詞彙「{self.word}」，無法更新。",
                ephemeral=True
            )