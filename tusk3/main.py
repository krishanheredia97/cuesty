import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import firebase_admin
from firebase_admin import credentials, db

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
TOKEN2 = os.getenv('TUSK_TOKEN')
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')
REVIEW_QUEST_CHANNEL_ID = 1245264665315901460

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


import logging

@bot.event
async def on_interaction(interaction):
    if interaction.data['custom_id'] == 'send_to_review':
        from data_manager import load_quest_data, save_quest_data
        channel = bot.get_channel(REVIEW_QUEST_CHANNEL_ID)

        quest_id = interaction.channel.name
        quest_data = load_quest_data(quest_id)
        quest_data['Quest_Main']['quest_status'] = 'in review'
        save_quest_data(quest_data)
        await interaction.response.send_message(f"Quest {quest_id} has been sent for review.")
        await interaction.channel.delete()

        thread = await channel.create_thread(name=quest_id, type=discord.ChannelType.public_thread)
        from frontend.discord_frontend.ui_View.accepted_denied_buttons import ReviewActionButtons
        await thread.send(f"Review the quest {quest_id}:", view=ReviewActionButtons())


    elif interaction.data['custom_id'] in ['accepted', 'denied']:
        from data_manager import load_quest_data, save_quest_data
        quest_id = interaction.channel.name
        quest_data = load_quest_data(quest_id)
        new_status = 'accepted' if interaction.data['custom_id'] == 'accepted' else 'denied'
        quest_data['Quest_Main']['quest_status'] = new_status
        save_quest_data(quest_data)
        await interaction.response.send_message(f"Quest {quest_id} status has been updated to {new_status}.")
        await interaction.channel.delete()


bot.run(TOKEN2)
