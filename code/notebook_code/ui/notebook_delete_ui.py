import discord
from ..notebook_delete import delete_word

class DeleteNoteModal(discord.ui.Modal, title = "刪除詞彙"):
    japanese = discord.ui.TextInput(label = "日文")

    async def on_submit(self, interaction: discord.Interaction):
        flag = delete_word(str(interaction.user.id), self.japanese)
        
        if (flag):
            await interaction.response.send_message(f"✅ 已將詞彙「{self.japanese}」從你的學習本刪除！")
        else:
            await interaction.response.send_message(f"⚠️ 詞彙「{self.japanese}」未在學習本中。")