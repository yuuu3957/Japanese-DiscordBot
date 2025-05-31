import discord
import NoteBook
import random
import groq_help

model, client = groq_help.start_groq()

class QuizCountModal(discord.ui.Modal):
    def __init__(self,type):
        super().__init__(title="設定測驗題數")
        self.num_questions = discord.ui.TextInput(
            label="請輸入測驗題數（1~25）",
            placeholder="輸入數字",
            required=True,
            max_length=2
        )
        self.add_item(self.num_questions)
        self.type = type

    async def on_submit(self, interaction: discord.Interaction):
        try:
            num = int(self.num_questions.value)
            if num < 1:
                num = 1
            elif num > 25:
                num = 25
            await interaction.response.send_message(f"你設定了 {num} 題，請從下拉選單選擇題目。", ephemeral=True)
            # 觸發下一步選擇題目
            view = QuizSelectView(num, interaction.user.id, self.type)
            await interaction.followup.send("請選擇題目：", view=view, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("輸入錯誤，請輸入1到25之間的數字。", ephemeral=True)

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

class QuizSelectView(discord.ui.View):
    def __init__(self, num_questions, user_id, type):
        super().__init__()
        self.user_id = user_id
        # 讀取使用者詞庫
        full_word_list = NoteBook.load_user_notebook(str(user_id))
        # 隨機選題
        self.words = get_quiz_words(full_word_list, num_questions)
        # 建立選單
        if type == "日譯中":
            self.select = JtoC_QuizSelect(self.words, num_questions)
        else:
            self.select = CtoJ_QuizSelect(self.words, num_questions)
        self.add_item(self.select)

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
        correct = groq_help.generate_japanese_quiz(user_answer, self.select_word, model,client)

        if correct:
            await interaction.response.send_message("答對了！🎉", ephemeral=True)
        else:
            await interaction.response.send_message(f"答錯了，正確答案是：{correct_answer}", ephemeral=True)
        
        update_user_word_result(self.user_id, self.word_data["japanese"], "jp_to_ch", correct)

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


        

def get_quiz_words(notebook, num_questions):
    # 篩出未學詞彙
    unlearned = [w for w in notebook if w.get("status") == "未學"]
    learned = [w for w in notebook if w.get("status") == "已學"]

    if len(unlearned) >= num_questions:
        # 從未學詞彙中隨機抽題
        return random.sample(unlearned, num_questions)
    else:
        # 未學不夠，先全拿未學，再從已學補足
        needed = num_questions - len(unlearned)
        sampled_learned = random.sample(learned, min(needed, len(learned)))
        return unlearned + sampled_learned

def update_quiz_result(word_data, direction, correct):
    """
    word_data: 詞彙 dict
    direction: 'jp_to_ch' 或 'ch_to_jp'
    correct: True or False
    """
    if "quiz_results" not in word_data:
        word_data["quiz_results"] = {"jp_to_ch": {"correct":0, "wrong":0}, "ch_to_jp": {"correct":0, "wrong":0}}

    if correct:
        word_data["quiz_results"][direction]["correct"] += 1
    else:
        word_data["quiz_results"][direction]["wrong"] += 1

    # 簡單判斷學習狀態
    corrects = word_data["quiz_results"]["jp_to_ch"]["correct"] and word_data["quiz_results"]["ch_to_jp"]["correct"]
    if corrects:
        word_data["status"] = "已學"
    else:
        word_data["status"] = "未學"

def update_user_word_result(user_id, japanese_word, direction, correct):
    notebook = NoteBook.load_user_notebook(user_id)
    for word in notebook:
        if word.get("japanese") == japanese_word:
            update_quiz_result(word, direction, correct)
            NoteBook.save_user_notebook(user_id, notebook)
            return True
    return False  # 找不到該詞彙