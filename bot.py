import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import data_manager  # Import data_manager here as well to pass it correctly
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
        habit_name = self.children[0].value.strip()[:30]  # Limit habit name to 30 characters
        success, message = self.user.add_habit(habit_name, data_manager)
        await interaction.response.send_message(message, ephemeral=True)

class AddHabitButton(Button):
    def __init__(self):
        super().__init__(label="Add Habit", style=discord.ButtonStyle.green, custom_id="add_habit_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        await interaction.response.send_modal(HabitModal(user))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.purge()
        view = View()
        view.add_item(AddHabitButton())
        await channel.send("Click to add a habit:", view=view)

bot.run(TOKEN)
