import discord
from .quiz_CtoJ_ui import CtoJ_QuizSelect
from .quiz_JtoC_ui import JtoC_QuizSelect
from ..quiz_base import get_quiz_words, check_num

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
            modal = QuizCountModal("日譯中")
            await interaction.response.send_modal(modal)

    @discord.ui.button(label="中譯日", style=discord.ButtonStyle.danger)
    async def ch_to_jp_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = QuizCountModal("中譯日")
            await interaction.response.send_modal(modal)

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
            else :
                num = check_num(str(interaction.user.id), num)
                
            await interaction.response.send_message(f"你設定了 {num} 題，請從下拉選單選擇題目。", ephemeral=True)
            # 觸發下一步選擇題目
            view = QuizSelectView(num, interaction.user.id, self.type)
            await interaction.followup.send("請選擇題目：", view=view, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("輸入錯誤，請輸入1到25之間的數字。", ephemeral=True)

class QuizSelectView(discord.ui.View):
    def __init__(self, num_questions, user_id, type):
        super().__init__()
        self.user_id = user_id
        # 隨機選題
        self.words = get_quiz_words(str(user_id), num_questions)
        # 建立選單
        if type == "日譯中":
            self.select = JtoC_QuizSelect(self.words, num_questions)
        else:
            self.select = CtoJ_QuizSelect(self.words, num_questions)
        self.add_item(self.select)