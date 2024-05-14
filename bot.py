import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput, Select
from user import User
import os

TOKEN = os.getenv('Cuesty_Discord_Bot')
CHANNEL_ID = 1238187584434339957  # ID of the channel to send the initial message

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


class ViceModal(Modal):
    def __init__(self, user):
        super().__init__(title="Add a New Vice")
        self.user = user
        self.add_item(TextInput(label="Vice Name", placeholder="Enter the vice you want to manage"))

    async def on_submit(self, interaction: discord.Interaction):
        vice_name = self.children[0].value.strip()[:30]
        success, message = self.user.add_vice(vice_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_buttons(interaction)


class AddViceButton(Button):
    def __init__(self):
        super().__init__(label="Add Vice", style=discord.ButtonStyle.blurple, custom_id="add_vice_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        await interaction.response.send_modal(ViceModal(user))


class RelapseSelect(Select):
    def __init__(self, user):
        self.user = user
        options = [discord.SelectOption(label=vice) for vice in self.user.get_active_vices()]
        super().__init__(placeholder="Select a vice to mark as relapsed", options=options)

    async def callback(self, interaction: discord.Interaction):
        vice_name = self.values[0]
        success, message = self.user.relapse_vice(vice_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_buttons(interaction)


class RelapseButton(Button):
    def __init__(self):
        super().__init__(label="Relapse", style=discord.ButtonStyle.danger, custom_id="relapse_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        active_vices = user.get_active_vices()
        if not active_vices:
            await interaction.response.send_message("You have no active vices.", ephemeral=True)
            return

        view = View()
        view.add_item(RelapseSelect(user))
        await interaction.response.send_message("Select a vice to mark as relapsed:", view=view, ephemeral=True)
        await purge_and_resend_buttons(interaction)


class QuitSelect(Select):
    def __init__(self, user):
        self.user = user
        options = [discord.SelectOption(label=vice) for vice in self.user.get_inactive_vices()]
        super().__init__(placeholder="Select a vice to mark as active", options=options)

    async def callback(self, interaction: discord.Interaction):
        vice_name = self.values[0]
        success, message = self.user.quit_vice(vice_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_buttons(interaction)


class QuitButton(Button):
    def __init__(self):
        super().__init__(label="Quit", style=discord.ButtonStyle.green, custom_id="quit_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        inactive_vices = user.get_inactive_vices()
        if not inactive_vices:
            await interaction.response.send_message("You have no inactive vices.", ephemeral=True)
            return

        view = View()
        view.add_item(QuitSelect(user))
        await interaction.response.send_message("Select a vice to mark as active:", view=view, ephemeral=True)
        await purge_and_resend_buttons(interaction)


class UserHistoryButton(Button):
    def __init__(self):
        super().__init__(label="Show History", style=discord.ButtonStyle.secondary, custom_id="history_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        embed = discord.Embed(title=f"{user.data['username']}'s Vice History", color=discord.Color.blue())

        for vice in user.data["vices"]:
            vice_log = ""
            for log_entry in vice.log:
                vice_log += f"{log_entry['action'].capitalize()} on {log_entry['timestamp']}\n"
            embed.add_field(name=vice.name, value=vice_log or "No actions recorded.", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await purge_and_resend_buttons(interaction)



async def purge_and_resend_buttons(interaction):
    channel = interaction.channel
    await channel.purge()
    view = View()
    view.add_item(QuitButton())
    view.add_item(RelapseButton())
    view.add_item(AddViceButton())
    view.add_item(UserHistoryButton())
    await channel.send("Click to add, relapse, or view history of vices:", view=view)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.purge()
        view = View()
        view.add_item(QuitButton())
        view.add_item(RelapseButton())
        view.add_item(AddViceButton())
        view.add_item(UserHistoryButton())
        await channel.send("Click to add, relapse, or view history of vices:", view=view)


bot.run(TOKEN)
