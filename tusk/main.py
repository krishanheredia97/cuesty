# main.py
import discord
import logging
from discord.ext import commands
from tusk_proposals import bot, TOKEN2, CREATE_QUEST_CHANNEL_ID, CreateQuestView
from tusk_accepted_quests import handle_accepted_quest

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}!')
    await initialize_create_quest_channel()  # Initialize the quest creation channel

async def initialize_create_quest_channel():
    try:
        channel = bot.get_channel(CREATE_QUEST_CHANNEL_ID)
        if channel:
            await channel.purge()
            await channel.send("Click the button below to create a new quest thread:", view=CreateQuestView())
        else:
            logging.error(f"Channel with ID {CREATE_QUEST_CHANNEL_ID} not found.")
    except discord.Forbidden:
        logging.error(f"Missing permissions to send messages in the channel with ID {CREATE_QUEST_CHANNEL_ID}.")
    except discord.HTTPException as e:
        logging.error(f"An error occurred: {e}")

bot.run(TOKEN2)
