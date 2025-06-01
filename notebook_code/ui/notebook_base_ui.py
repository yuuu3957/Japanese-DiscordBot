import discord
from ..notebook_base import load_user_notebook
from .notebook_add_ui import AddNoteModal
from .notebook_delete_ui import DeleteNoteModal
from .notebook_show_ui import ShowView
from .notebook_edit_ui import PagedView


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
        modal = AddNoteModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DeleteNoteModal()
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
        notebook = load_user_notebook(self.user_id)
        paged_view = PagedView(notebook)
        await interaction.response.send_message(
            "請從下拉選單選擇要編輯的詞彙：",
            view=paged_view,
            ephemeral=True
        )
