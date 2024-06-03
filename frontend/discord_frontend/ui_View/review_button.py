import discord


class ReviewButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Send to Review", style=discord.ButtonStyle.green, custom_id="send_to_review"))
        self.add_item(discord.ui.Button(label="Continue Editing", style=discord.ButtonStyle.grey, custom_id="continue_editing"))
