import discord
from ..quiz_base import update_user_word_result

class CtoJ_QuizSelect(discord.ui.Select):
    def __init__(self, words, num_questions):
        self.words = words
        self.num_questions = num_questions
        options = [
            discord.SelectOption(label=w["chinese"], description="", value=w["chinese"])
            for w in words[:25]  # Discord最多25個選項
        ]
        super().__init__(placeholder="選擇要回答的題目", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_word = self.values[0]
        # 找到選中的詞彙資料
        word_data = next((w for w in self.words if w["chinese"] == selected_word), None)
        if not word_data:
            await interaction.response.send_message("找不到該題目資料。", ephemeral=True)
            return

        modal = CtoJ_QuizAnswerModal(word_data, interaction.user.id)
        await interaction.response.send_modal(modal)

class CtoJ_QuizAnswerModal(discord.ui.Modal):
    def __init__(self, word_data, user_id):        
        if len(word_data["chinese"]) <= 35:
            chinese = word_data["chinese"]
        else:
            chinese =  word_data["chinese"][:35].rstrip() + "..."

        super().__init__(title=f"請翻譯：「{chinese}」")
        self.word_data = word_data
        self.user_id = user_id
        self.answer = discord.ui.TextInput(label="你的日文答案", style=discord.TextStyle.paragraph)
        self.add_item(self.answer)

    async def on_submit(self, interaction: discord.Interaction):
        user_answer = self.answer.value.strip()
        correct_answer = self.word_data.get("japanese", "").strip()
        if user_answer == correct_answer:
            correct = True
            await interaction.response.send_message("答對了！🎉", ephemeral=True)
        else:
            correct = False
            await interaction.response.send_message(f"答錯了，正確答案是：{correct_answer}", ephemeral=True)

        update_user_word_result(self.user_id, self.word_data["japanese"], "ch_to_jp", correct)
