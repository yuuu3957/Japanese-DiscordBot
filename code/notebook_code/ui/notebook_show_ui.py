import discord
from ..notebook_base import load_user_notebook

Notebook_Page_Size = 3

class ShowView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.notebook = load_user_notebook(user_id)
        self.user_id = user_id
        self.cur_page = 0
        self.max_page = (len(self.notebook) - 1) // Notebook_Page_Size

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
                    value += f"例句{i}：{jp_sentence}\n"
                    if jp_reading:
                        value += f" ({jp_reading})"
                    value += "\n"
                else:
                    # 如果 jp_sentence 是空字串，就只輸出空行或略過
                    continue

                value += f"翻譯{i}：{chinese_translation}\n"
            embed.add_field(name=name, value=value, inline=False)
        return embed

    async def update_message(self, interaction):
        # 更新按鈕狀態
        self.prev_page.disabled = self.cur_page == 0
        self.next_page.disabled = self.cur_page == self.max_page
        # 編輯訊息
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="上一頁", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if int(interaction.user.id) != int(self.user_id):
            await interaction.response.send_message("這不是你的學習本喔！", ephemeral=True)
            return
        if self.cur_page > 0:
            self.cur_page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("已經是第一頁了。", ephemeral=True)

    @discord.ui.button(label="下一頁", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if int(interaction.user.id) != int(self.user_id):
            await interaction.response.send_message("這不是你的學習本喔！", ephemeral=True)
            return
        if self.cur_page < self.max_page:
            self.cur_page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("已經是最後一頁了。", ephemeral=True)