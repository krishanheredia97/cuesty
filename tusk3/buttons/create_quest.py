import discord
import json
import logging
import re
from data_manager import save_quest_data
from firebase_admin import db

CREATE_QUEST_CHANNEL_ID = 1243061918080438272

with open('config/quest_default_config.json', 'r') as file:
    QUEST_DEFAULT_CONFIG = json.load(file)

# Store the reward_config globally
REWARD_CONFIG = QUEST_DEFAULT_CONFIG


class CreateQuestView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(CreateQuestButton(bot))


class CreateQuestButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Create Quest", style=discord.ButtonStyle.blurple, custom_id="create_quest_button")
        self.bot = bot  # Store the bot instance

    async def callback(self, interaction: discord.Interaction):
        creator = interaction.user.name

        # Get the initial quest data from quest_data.py
        from tusk3.config.quest_data import get_initial_quest_data
        quest_data = get_initial_quest_data(creator)

        # Set default values
        from utils.quest_default_configurator import set_default_values
        default_values = set_default_values()
        quest_data['Quest_Requirements'].update(default_values)

        # Save the quest data to Firebase
        save_quest_data(quest_data)

        # Create a thread in the channel
        quest_id = quest_data["Quest_Main"]["quest_id"]
        thread = await interaction.channel.create_thread(name=quest_id, type=discord.ChannelType.public_thread)
        await thread.send(f"Ah, {interaction.user.mention}, I see you want to arrange a new quest. "
                          f"I'm ready for the quest instructions!")


async def initialize_create_quest_channel(bot):
    try:
        channel = bot.get_channel(CREATE_QUEST_CHANNEL_ID)
        if channel:
            await channel.purge()
            await channel.send("Click the button below to create a new quest thread:", view=CreateQuestView(bot))
        else:
            logging.error(f"Channel with ID {CREATE_QUEST_CHANNEL_ID} not found.")
    except discord.Forbidden:
        logging.error(f"Missing permissions to send messages in the channel with ID {CREATE_QUEST_CHANNEL_ID}.")
    except discord.HTTPException as e:
        logging.error(f"An error occurred: {e}")


async def handle_thread_message(message):
    # Extract the quest_id from the thread name
    quest_id = message.channel.name

    # Regex to parse each line in the message
    pattern = re.compile(r"#(\w+):\s*\[(.+)\]")

    # Split the message into lines and process each line
    updates = {}
    for line in message.content.split('\n'):
        match = pattern.match(line)
        if match:
            item, value = match.groups()
            from tusk3.config.quest_data_manager import get_quest_item_path

            # Validate quest_duration_cat values
            if item == "quest_duration_cat" and value not in ['d', 'w', 'm', 'y']:
                await message.channel.send("Invalid value for quest_duration_cat. Use 'd', 'w', 'm', or 'y'.")
                return

            item_path = get_quest_item_path(item)
            if item_path:
                if item != "quest_duration_days":  # Ensure quest_duration_days is not manually updated
                    updates[item_path] = value
            else:
                await message.channel.send(f"Item {item} not recognized.")
                return  # Exit if any item is not recognized

    if updates:
        # Handle special cases like quest_difficulty and duration calculation
        if 'Quest_Users/quest_difficulty' in updates:
            try:
                value = int(updates['Quest_Users/quest_difficulty'])
                from utils.quest_calculator import calculate_rewards
                from utils.quest_level_configurator import configure_level_requirements
                # Calculate the rewards based on difficulty
                rewards = calculate_rewards(value)
                # Configure level requirements
                requirements = configure_level_requirements(value)
                # Add calculated rewards and requirements to updates
                updates.update({
                    "Quest_Rewards/quest_xp_reward": rewards['xp_reward'],
                    "Quest_Rewards/quest_gp_reward": rewards['gp_reward'],
                    "Quest_Rewards/quest_honor_reward": rewards['honor_reward'],
                    "Quest_Requirements/quest_honor_cost": requirements['honor_cost'],
                    "Quest_Requirements/quest_minimum_level_requirement": requirements[
                        'quest_minimum_level_requirement'],
                    "Quest_Progress/quest_yellow_threshold": requirements['quest_yellow_threshold'],
                    "Quest_Progress/quest_green_threshold": requirements['quest_green_threshold'],
                    "Quest_Progress/quest_cyan_threshold": requirements['quest_cyan_threshold']
                })
            except ValueError:
                await message.channel.send("Invalid value for quest_difficulty. It should be an integer.")
                return

        # Calculate quest_duration_days if both quest_duration_cat and quest_duration_num are provided
        if 'Quest_Time/quest_duration_cat' in updates and 'Quest_Time/quest_duration_num' in updates:
            try:
                from utils.quest_days_calculator import calculate_duration_days
                duration_cat = updates['Quest_Time/quest_duration_cat']
                duration_num = int(updates['Quest_Time/quest_duration_num'])
                duration_days = calculate_duration_days(duration_cat, duration_num)
                updates['Quest_Time/quest_duration_days'] = duration_days
            except ValueError as e:
                await message.channel.send(f"Error in calculating duration days: {e}")
                return

        # Update the quest in the database
        ref = db.reference(f'quests/{quest_id}')
        ref.update(updates)
        await message.channel.send(f"Updated the quest with the following values:\n" +
                                   "\n".join([f"{k}: {v}" for k, v in updates.items()]))
    else:
        await message.channel.send("No valid updates found. Use #item: [value] format.")