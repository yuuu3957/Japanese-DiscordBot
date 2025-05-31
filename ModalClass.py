import discord
import NoteBook

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
        flag = NoteBook.save_word(str(interaction.user.id), word_data)
        if (flag):
            await interaction.response.send_message(f"✅ 已將詞彙「{word_data['japanese']}」加入你的學習本！")
        else:
            await interaction.response.send_message(f"⚠️ 詞彙「{word_data['japanese']}」已存在學習本中。")

class DeleteNoteModal(discord.ui.Modal, title = "刪除詞彙"):
    japanese = discord.ui.TextInput(label = "日文")

    async def on_submit(self, interaction: discord.Interaction):
        flag = NoteBook.delete_word(str(interaction.user.id), self.japanese)
        
        if (flag):
            await interaction.response.send_message(f"✅ 已將詞彙「{self.japanese}」從你的學習本刪除！")
        else:
            await interaction.response.send_message(f"⚠️ 詞彙「{self.japanese}」未在學習本中。")

class EditModal(discord.ui.Modal):
    def __init__(self, word, field):
        super().__init__(title=f"修改「{word}」的 {field} 資料")
        self.word = word
        self.field = field
        self.new_value = discord.ui.TextInput(label=f"請輸入新的 {field}：", style=discord.TextStyle.paragraph)
        self.add_item(self.new_value)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        notebook = NoteBook.load_user_notebook(user_id)

        # 尋找詞彙並修改欄位
        modified = False
        if self.field == "status":
            if self.new_value.value == "未學":
                for w in notebook:
                    if w["japanese"] == self.word:
                        w[self.field] = self.new_value.value
                        modified = True
                        w["quiz_results"] = {"jp_to_ch": {"correct":0, "wrong":0}, "ch_to_jp": {"correct":0, "wrong":0}}
                        break


        elif "example" not in self.field:
            for w in notebook:
                if w["japanese"] == self.word:
                    w[self.field] = self.new_value.value
                    modified = True
                    break
        elif "example1" in self.field:
            self.field = self.field[len("example1 "):]
            for w in notebook:
                if w["japanese"] == self.word:
                    w["examples"][0][self.field] = self.new_value.value
                    modified = True
                    break
        else:
            self.field = self.field[len("example2 "):]  
            for w in notebook:
                if w["japanese"] == self.word:
                    w["examples"][1][self.field] = self.new_value.value
                    modified = True
                    break

        if modified:
            NoteBook.save_user_notebook(user_id, notebook)
            await interaction.response.send_message(
                f"✅ 已成功將「{self.word}」的 {self.field} 更新為：{self.new_value.value}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ 找不到詞彙「{self.word}」，無法更新。",
                ephemeral=True
            )
    