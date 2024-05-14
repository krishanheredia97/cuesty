import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput, Select
from discord import SelectOption

# Set the bot command prefix, token, and channel ID
TOKEN = 'MTIzODE4MzM0NTc3MTI1Mzk1NQ.G82UYZ.CE8PEIbBJrawTxUb1wIhL3xDRxwWZOreEVuRx0'
CHANNEL_ID = '1238187584434339957'

# Define intents
intents = discord.Intents.default()
intents.messages = True  # Adjust based on your needs, e.g., if you need to track messages
intents.message_content = True  # Enable if your bot processes message content

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

class HabitModal(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(TextInput(label='Habit Name', placeholder='Enter the name of your new habit'))

    async def callback(self, interaction: discord.Interaction):
        # Habit creation logic
        await interaction.response.send_message(f'New habit added: {self.children[0].value}', ephemeral=True)

class HabitSelect(Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = [
            SelectOption(label='Habit 1', description='This is a placeholder for Habit 1'),
            SelectOption(label='Habit 2', description='This is a placeholder for Habit 2'),
        ]
        self.placeholder = 'Choose a habit to mark a relapse'
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        # Relapse logic
        await interaction.response.send_message(f'Relapse recorded for: {self.values[0]}', ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.purge()

    # Create buttons
    add_habit_button = Button(label='Add New Habit', style=discord.ButtonStyle.green)
    relapse_button = Button(label='Relapse', style=discord.ButtonStyle.red)

    # Create a view to hold the buttons
    view = View()
    view.add_item(add_habit_button)
    view.add_item(relapse_button)

    # Button callbacks
    async def add_habit_button_callback(interaction: discord.Interaction):
        modal = HabitModal(title='Add New Habit')
        await interaction.response.send_modal(modal)

    async def relapse_button_callback(interaction: discord.Interaction):
        select_view = View()
        select_view.add_item(HabitSelect())
        await interaction.response.send_message('Select a habit to mark as relapsed:', view=select_view, ephemeral=True)

    add_habit_button.callback = add_habit_button_callback
    relapse_button.callback = relapse_button_callback

    await channel.send('Manage your habits:', view=view)

# Run the bot
bot.run(TOKEN)
