import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
TOKEN2 = os.getenv('TUSK_TOKEN')

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}!')
    from tusk2.buttons.CreateQuest import initialize_create_quest_channel  # Deferred import
    await initialize_create_quest_channel(bot)

bot.run(TOKEN2)
