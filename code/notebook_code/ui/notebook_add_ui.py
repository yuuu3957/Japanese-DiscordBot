import discord
from ..notebook_add import add_word_to_notebook

class AddNoteModal(discord.ui.Modal, title = "新增詞彙"):
    japanese = discord.ui.TextInput(label = "日文")
    chinese = discord.ui.TextInput(label = "中文")
    reading = discord.ui.TextInput(label = "假名")
    example_jp_s = discord.ui.TextInput(label = "例句:",required=False)
    note = discord.ui.TextInput(label = "補充筆記",required=False)

    async def on_submit(self, interaction: discord.Interaction):
        word_data = {
            "japanese": self.japanese.value,
            "chinese": self.chinese.value,
            "reading": self.reading.value,
            "examples": [
            {
                "jp_sentence": self.example_jp_s.value,
                "jp_reading": "",
                "chinese_translation": ""
            },
            {
                "jp_sentence": "",
                "jp_reading": "",
                "chinese_translation": ""
            }
            ],
            "status": "未學",
            "quiz_results": {
                "jp_to_ch": {"correct": 0, "wrong": 0},
                "ch_to_jp": {"correct": 0, "wrong": 0}
            },
            "notes": self.note.value

        }
        flag = add_word_to_notebook(str(interaction.user.id), word_data)
        if (flag):
            await interaction.response.send_message(f"✅ 已將詞彙「{word_data['japanese']}」加入你的學習本！")
        else:
            await interaction.response.send_message(f"⚠️ 詞彙「{word_data['japanese']}」已存在學習本中。")