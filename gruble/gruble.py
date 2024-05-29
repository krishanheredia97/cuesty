import discord
import json
import os
from discord.ext import commands

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Bot token
GRUBLE_TOKEN = os.getenv('GRUBLE_TOKEN')

# Channel ID for quest tickets
QUEST_TICKETS_CHANNEL_ID = 1244040942995111986

# Initialize bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Path to quest data file
QUEST_DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'tusk', 'quest_data.json')

# Utility function to load quest data
def load_quest_data():
    with open(QUEST_DATA_FILE_PATH, 'r') as file:
        return json.load(file)

# Function to send quest ticket message
async def send_quest_ticket_message(quest, channel):
    quest_name = quest["quest_name"]
    xp_reward = quest["quest_xp_reward"]
    gp_reward = quest["quest_gp_reward"]
    honor_reward = quest["quest_honor_reward"]

    message_content = (
        f"**New Quest Available!**\n"
        f"**Quest Name:** {quest_name}\n"
        f"**XP Reward:** {xp_reward}\n"
        f"**GP Reward:** {gp_reward}\n"
        f"**Honor Reward:** {honor_reward}\n\n"
        f"Click the button below to purchase your entry ticket!"
    )

    view = PurchaseView(quest["quest_id"])
    await channel.send(message_content, view=view)

# Button for purchasing quest tickets
class PurchaseButton(discord.ui.Button):
    def __init__(self, quest_id):
        super().__init__(label="Purchase", style=discord.ButtonStyle.success, custom_id=f"purchase_{quest_id}")
        self.quest_id = quest_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # Handle the purchase logic here
        await interaction.followup.send("You have purchased an entry ticket to the quest!", ephemeral=True)

# View for the purchase button
class PurchaseView(discord.ui.View):
    def __init__(self, quest_id):
        super().__init__(timeout=None)
        self.add_item(PurchaseButton(quest_id))

# Event to notify when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

    # Load quest data and send messages for accepted quests
    quest_data = load_quest_data()
    channel = bot.get_channel(QUEST_TICKETS_CHANNEL_ID)

    if channel:
        for quest_id, quest in quest_data.items():
            await send_quest_ticket_message(quest, channel)

    else:
        print(f"Channel with ID {QUEST_TICKETS_CHANNEL_ID} not found.")

# Run the bot
bot.run(GRUBLE_TOKEN)
