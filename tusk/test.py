import os
from dotenv import load_dotenv
import discord
import firebase_admin
from discord.ext import commands
from discord.ui import Button, View
from data_manager import load_data, save_data
from firebase_admin import credentials, db
from datetime import datetime
from quest_data_manager import load_quest_data
import logging

# Load environment variables from .env file
load_dotenv()

# Get the path to the Firebase service account key JSON file from the environment variable
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')

# Initialize Firebase
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cuesty-424dc-default-rtdb.firebaseio.com/'
})

# Retrieve the bot token from the environment variable
TOKEN = os.getenv('TUSK_TOKEN')

# Intents are required for certain actions like reading member info
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

# Create a bot instance with specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Server ID where the category and channel will be created
SERVER_ID = 1238187583734022246
# Category ID to duplicate
CATEGORY_ID_TO_DUPLICATE = 1245263224480202883
# Channels to duplicate and their new names
CHANNELS_TO_DUPLICATE = {
    1245372881014100099: '🟡│task-check-in',
    1245263225751339088: '📜│quest-info',
    1245371676334489610: '🐎│battlefield',
    1245371990731264010: '🔥│bonfire'
}
# Bot's role ID
BOT_ROLE_ID = 1245506986834001992

async def handle_accepted_quest(guild: discord.Guild, quest_id: str):
    # Load quest data from quest_data_manager
    quest_data = load_quest_data()

    quest_id = str()
    # Check if the quest_id is in the quest data
    if quest_id not in quest_data:
        logging.info(f"Quest ID {quest_id} not found in quest data.")
        return None, None

    # Retrieve quest name and quest code from quest data
    quest_name = quest_data[quest_id]["Quest_Main"]["quest_name"]
    quest_code = quest_data[quest_id]["Quest_Main"]["quest_id"]


    # Fetch the bot's member object
    bot_member = guild.get_member(bot.user.id)
    if not bot_member:
        return

    # Check initial permissions
    permissions = bot_member.guild_permissions
    if permissions.manage_channels and permissions.manage_roles:
        try:
            # Create a new role
            new_role = await guild.create_role(name=quest_code)
            print(f"Created role ID: {new_role.id}")

            # Fetch the category to duplicate
            original_category = guild.get_channel(CATEGORY_ID_TO_DUPLICATE)
            if not original_category or not isinstance(original_category, discord.CategoryChannel):
                return

            # Duplicate the category with its permissions and rename it
            new_category = await guild.create_category(
                name=(f"🏰│{quest_name}"),
                overwrites=original_category.overwrites
            )

            # List to hold all new channel IDs
            new_channel_ids = [new_category.id]

            # Duplicate each specified channel inside the new category with the new name
            for original_channel_id, new_channel_name in CHANNELS_TO_DUPLICATE.items():
                original_channel = guild.get_channel(original_channel_id)
                if original_channel and isinstance(original_channel, discord.TextChannel):
                    new_channel = await new_category.create_text_channel(
                        name=new_channel_name,
                        overwrites=original_channel.overwrites,
                        topic=original_channel.topic,
                        nsfw=original_channel.nsfw,
                        slowmode_delay=original_channel.slowmode_delay
                    )
                    new_channel_ids.append(new_channel.id)

                    # Send buttons to the '🟡│task-check-in' channel
                    if new_channel_name == '🟡│task-check-in':
                        await send_task_check_in_buttons(new_channel)

            # Print the list of new channel IDs
            print(f"Created category and channel IDs: {new_channel_ids}")

        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

# Function to send task check-in buttons
async def send_task_check_in_buttons(channel):
    class TaskCheckInView(View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
        async def yes_button_callback(self, interaction, button):
            await update_user_progress(interaction.user.id, 'yes')
            await interaction.response.send_message("You clicked Yes!", ephemeral=True)

        @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
        async def no_button_callback(self, interaction, button):
            await update_user_progress(interaction.user.id, 'no')
            await interaction.response.send_message("You clicked No!", ephemeral=True)

    view = TaskCheckInView()
    await channel.send("Did you complete your task today?", view=view)

# Function to update user progress in Firebase
async def update_user_progress(user_id, response):
    data = load_data(user_id)
    if 'quest_individual_progress' not in data:
        data['quest_individual_progress'] = {
            'quest_individual_success_log': {'count': 0, 'timestamps': []},
            'quest_individual_failure_log': {'count': 0, 'timestamps': []}
        }
    timestamp = datetime.utcnow().isoformat()
    if response == 'yes':
        data['quest_individual_progress']['quest_individual_success_log']['count'] += 1
        data['quest_individual_progress']['quest_individual_success_log']['timestamps'].append(timestamp)
    else:
        data['quest_individual_progress']['quest_individual_failure_log']['count'] += 1
        data['quest_individual_progress']['quest_individual_failure_log']['timestamps'].append(timestamp)
    save_data(data)

@bot.event
async def on_ready():
    # Fetch the guild (server) using the SERVER_ID
    guild = bot.get_guild(SERVER_ID)
    if guild:
        await handle_accepted_quest(guild)


