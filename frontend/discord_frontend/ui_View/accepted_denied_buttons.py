import discord


class ReviewActionButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Accepted", style=discord.ButtonStyle.green, custom_id="accepted"))
        self.add_item(discord.ui.Button(label="Denied", style=discord.ButtonStyle.red, custom_id="denied"))