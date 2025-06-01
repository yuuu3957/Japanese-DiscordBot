import discord
from ..quiz_base import update_user_word_result
from ..quiz_groq import generate_japanese_quiz
from groq_help import start_groq

model, client = start_groq()

class JtoC_QuizSelect(discord.ui.Select):
    def __init__(self, words, num_questions):
        self.words = words
        self.num_questions = num_questions
        options = [
            discord.SelectOption(label=w["japanese"], description="", value=w["japanese"])
            for w in words[:25]  # Discord最多25個選項
        ]
        super().__init__(placeholder="選擇要回答的題目", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_word = self.values[0]
        # 找到選中的詞彙資料
        word_data = next((w for w in self.words if w["japanese"] == selected_word), None)
        if not word_data:
            await interaction.response.send_message("找不到該題目資料。", ephemeral=True)
            return

        modal = JtoC_QuizAnswerModal(word_data, interaction.user.id, selected_word)
        await interaction.response.send_modal(modal)

class JtoC_QuizAnswerModal(discord.ui.Modal):
    def __init__(self, word_data, user_id, select_word):
        super().__init__(title=f"請翻譯日文詞彙：「{word_data['japanese']}」")
        self.word_data = word_data
        self.user_id = user_id
        self.select_word = select_word
        self.answer = discord.ui.TextInput(label="你的中文答案", style=discord.TextStyle.paragraph)
        self.add_item(self.answer)

    async def on_submit(self, interaction: discord.Interaction):
        user_answer = self.answer.value.strip()
        correct_answer = self.word_data.get("chinese", "").strip()
        correct = generate_japanese_quiz(user_answer, self.select_word, model,client)

        if correct:
            await interaction.response.send_message("答對了！🎉", ephemeral=True)
        else:
            await interaction.response.send_message(f"答錯了，正確答案是：{correct_answer}", ephemeral=True)
        
        update_user_word_result(self.user_id, self.word_data["japanese"], "jp_to_ch", correct)