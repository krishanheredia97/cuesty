import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput, Select
import data_manager
from user import User
import os

TOKEN = os.getenv('Cuesty_Discord_Bot')
CHANNEL_ID = 1238187584434339957

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


class HabitModal(Modal):
    def __init__(self, user):
        super().__init__(title="Add a New Habit")
        self.user = user
        self.add_item(TextInput(label="Habit Name", placeholder="Enter the habit you want to manage"))

    async def on_submit(self, interaction: discord.Interaction):
        habit_name = self.children[0].value.strip()[:30]
        success, message = self.user.add_habit(habit_name, data_manager)
        await interaction.response.send_message(message, ephemeral=True)


class AddHabitButton(Button):
    def __init__(self):
        super().__init__(label="Add Habit", style=discord.ButtonStyle.green, custom_id="add_habit_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        await interaction.response.send_modal(HabitModal(user))


class RelapseSelect(Select):
    def __init__(self, user):
        self.user = user
        options = [discord.SelectOption(label=habit) for habit in self.user.get_active_habits()]
        super().__init__(placeholder="Select a habit to mark as relapsed", options=options)

    async def callback(self, interaction: discord.Interaction):
        habit_name = self.values[0]
        success, message = self.user.relapse_habit(habit_name)
        await interaction.response.send_message(message, ephemeral=True)


class RelapseButton(Button):
    def __init__(self):
        super().__init__(label="Relapse", style=discord.ButtonStyle.danger, custom_id="relapse_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        active_habits = user.get_active_habits()
        if not active_habits:
            await interaction.response.send_message("You have no active habits.", ephemeral=True)
            return

        view = View()
        view.add_item(RelapseSelect(user))
        await interaction.response.send_message("Select a habit to mark as relapsed:", view=view, ephemeral=True)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.purge()
        view = View()
        view.add_item(AddHabitButton())
        view.add_item(RelapseButton())
        await channel.send("Click to add or relapse a habit:", view=view)


bot.run(TOKEN)
