import discord
import json
import logging
from datetime import datetime, timezone
from discord.ext import commands
from tusk2.quest_data_manager import load_quest_data, save_quest_data
from utils.generate_unique_id import generate_unique_id

CREATE_QUEST_CHANNEL_ID = 1243061918080438272

with open('quest_default_config.json', 'r') as file:
    QUEST_DEFAULT_CONFIG = json.load(file)


class CreateQuestView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(CreateQuestButton(bot))


class CreateQuestButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Create Quest", style=discord.ButtonStyle.blurple, custom_id="create_quest_button")
        self.bot = bot  # Store the bot instance

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        thread_name = f"Q - {generate_unique_id()}"
        threads_channel = interaction.guild.get_channel(CREATE_QUEST_CHANNEL_ID)

        if not isinstance(threads_channel, discord.TextChannel):
            await interaction.followup.send("The configured channel for creating threads is not a text channel.",
                                            ephemeral=True)
            return

        thread = await threads_channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
        creator = interaction.user
        timestamp = datetime.now(timezone.utc).isoformat()

        quest_data = load_quest_data()

        quest_id = str(thread.id)
        if quest_id not in quest_data:
            quest_data[quest_id] = {
                "Quest_Main": {
                    "quest_id": thread_name.split(" - ")[1],
                    "timestamp": timestamp,
                    "quest_status": "draft",
                    "quest_name": None,
                    "quest_real_goal": None,
                    "quest_difficulty": None,
                    "quest_type": None,
                    "quest_daily_instances": 1
                },
                "Quest_Narrative": {
                    "quest_fict_goal": None,
                    "quest_stage": None,
                    "quest_enemy": None,
                },
                "Quest_Time": {
                    "quest_duration_cat": None,
                    "quest_duration_num": None,
                    "quest_duration_weeks": None,
                    "quest_start_date": None,
                    "quest_end_date": None,
                    "quest_completion_time": None,
                },
                "Quest_Rewards": {
                    "quest_xp_reward": None,
                    "quest_gp_reward": None,
                    "quest_honor_reward": None,
                    "quest_item_reward": None,
                },
                "Quest_Users": {
                    "quest_creator": creator.name,
                    "quest_participants": [],
                    "quest_enrolled_users": [],
                    "quest_validator": None,
                    "quest_total_users": len("quest_participants")
                },
                "Quest_Requirements": {
                    "quest_minimum_level_requirement": None,
                    "quest_honor_cost": None,
                    "quest_item_requirement": None,
                    "quest_minimum_enrolled_users": QUEST_DEFAULT_CONFIG["default_values"][
                        "quest_minimum_enrolled_users"],
                    "quest_type": QUEST_DEFAULT_CONFIG["default_values"]["quest_type"]
                },
                "Quest_Progress": {
                    "quest_daily_perfect_count": None,
                    "quest_overall_perfect_count": None,
                    "quest_users_success_count": None,
                    "quest_users_failure_count": None,
                    "quest_users_unreported_count": None,
                    "quest_current_day": None,
                    "quest_current_instance": None,
                    "quest_daily_success_rate": None,
                    "quest_overall_success_rate": None
                }
            }

            save_quest_data(quest_data)

        await thread.send(f"Ah, {creator.mention}, I see you want to arrange a new quest. "
                          f"I'm ready for the quest instructions!")

        # Print the thread's ID
        print(f"Thread ID: {thread.id}")

        # Start listening for messages in the thread
        self.bot.loop.create_task(start_thread_listener(self.bot, thread.id))


async def initialize_create_quest_channel(bot):
    try:
        channel = bot.get_channel(CREATE_QUEST_CHANNEL_ID)
        if channel:
            await channel.purge()
            await channel.send("Click the button below to create a new quest thread:",
                               view=CreateQuestView(bot))  # Pass the bot instance
        else:
            logging.error(f"Channel with ID {CREATE_QUEST_CHANNEL_ID} not found.")
    except discord.Forbidden:
        logging.error(f"Missing permissions to send messages in the channel with ID {CREATE_QUEST_CHANNEL_ID}.")
    except discord.HTTPException as e:
        logging.error(f"An error occurred: {e}")


# New function to listen for messages in the created thread
async def start_thread_listener(bot, thread_id):
    @bot.event
    async def on_message(message):
        if message.channel.id != thread_id:
            return

        if message.author.bot:
            return

        # Parse the message content
        update_data = parse_quest_message(message.content)

        if update_data:
            # Load current quest data
            quest_data = load_quest_data()
            quest_id = str(thread_id)

            if quest_id in quest_data:
                update_quest_data(quest_data[quest_id], update_data)
                save_quest_data(quest_data)
                await message.channel.send("Quest data updated successfully!")
            else:
                await message.channel.send("Quest data not found.")


def parse_quest_message(content):
    lines = content.split('\n')
    update_data = {}

    for line in lines:
        if line.startswith('#quest_'):
            key, value = line.split(':', 1)
            key = key.strip('# ')
            value = value.strip('[] ')
            update_data[key] = value

    return update_data


def update_quest_data(quest_data, update_data):
    for key, value in update_data.items():
        if key in quest_data["Quest_Main"]:
            quest_data["Quest_Main"][key] = value
        elif key in quest_data["Quest_Narrative"]:
            quest_data["Quest_Narrative"][key] = value
        elif key in quest_data["Quest_Time"]:
            quest_data["Quest_Time"][key] = value
        elif key in quest_data["Quest_Rewards"]:
            quest_data["Quest_Rewards"][key] = value
        elif key in quest_data["Quest_Users"]:
            quest_data["Quest_Users"][key] = value
        elif key in quest_data["Quest_Requirements"]:
            quest_data["Quest_Requirements"][key] = value
        elif key in quest_data["Quest_Progress"]:
            quest_data["Quest_Progress"][key] = value
