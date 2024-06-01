import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import firebase_admin
from firebase_admin import credentials

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
TOKEN2 = os.getenv('TUSK_TOKEN')
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')

cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cuesty-424dc-default-rtdb.firebaseio.com/'
})

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}!')
    from tusk3.buttons.create_quest import initialize_create_quest_channel
    await initialize_create_quest_channel(bot)

@bot.event
async def on_message(message):
    # Check if the message is in a thread and the author is not the bot itself
    if isinstance(message.channel, discord.Thread) and not message.author.bot:
        from tusk3.buttons.create_quest import handle_thread_message
        await handle_thread_message(message)
    await bot.process_commands(message)


bot.run(TOKEN2)
