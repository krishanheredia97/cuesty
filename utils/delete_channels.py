import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the environment variable
TOKEN = os.getenv('TUSK_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))

# Intents are required for certain actions like reading member info
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

# Create a bot instance with specified intents
bot = commands.Bot(command_prefix='!', intents=intents)


async def delete_channels():
    await bot.wait_until_ready()
    guild = bot.get_guild(SERVER_ID)

    # Ask for input inside PyCharm
    channel_ids_input = input("Please enter the list of channel IDs to delete, separated by commas: ")
    channel_ids_input = channel_ids_input.strip('[]')  # Remove square brackets if present
    channel_ids = [int(cid.strip()) for cid in channel_ids_input.split(',')]

    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.delete()
            print(f"Deleted channel: {channel_id}")

    await bot.close()


# Run the delete_channels coroutine after the bot is ready
@bot.event
async def on_ready():
    await delete_channels()


# Start the bot
bot.run(TOKEN)
