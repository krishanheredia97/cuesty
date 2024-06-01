import discord
import json
import logging
from datetime import datetime, timezone
from discord.ext import commands
from tusk2.quest_data_manager import load_quest_data, save_quest_data
from utils.generate_unique_id import generate_unique_id
from tusk2.classes.quest_class import Quest

CREATE_QUEST_CHANNEL_ID = 1243061918080438272

with open('quest_default_config.json', 'r') as file:
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
        await interaction.response.defer(ephemeral=True)
        quest_data = load_quest_data()

        quest_dict = quest_data.get(self.quest_id)
        if not quest_dict:
            await interaction.followup.send("Quest data not found.", ephemeral=True)
            return

        quest_data[self.quest_id]["Quest_Main"]["quest_status"] = "in review"
        save_quest_data(quest_data)

        # Convert dictionary to Quest object
        quest = Quest(
            quest_id=self.quest_id,
            quest_name=quest_dict["Quest_Main"]["quest_name"],
            quest_real_goal=quest_dict["Quest_Main"]["quest_real_goal"],
            quest_fict_goal=quest_dict["Quest_Narrative"]["quest_fict_goal"],
            quest_cutscene=quest_dict["Quest_Narrative"]["quest_cutscene"],
            quest_stage=quest_dict["Quest_Narrative"]["quest_stage"],
            quest_item_reward=quest_dict["Quest_Rewards"]["quest_item_reward"],
            quest_duration_weeks=quest_dict["Quest_Time"]["quest_duration_weeks"],
            quest_enemy=quest_dict["Quest_Narrative"]["quest_enemy"],
            quest_difficulty=quest_dict["Quest_Main"]["quest_difficulty"],
            #reward_config=QUEST_DEFAULT_CONFIG
        )
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
            quest = Quest(
                quest_id=thread_name.split(" - ")[1],
                creator_name=creator.name,
                timestamp=timestamp,
                #reward_config=REWARD_CONFIG  # Use the global REWARD_CONFIG
            )
            quest_data[quest_id] = quest.__dict__

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
                quest_dict = quest_data[quest_id]
                quest = Quest(
                    quest_id=quest_id,
                    creator_name=quest_dict["quest_creator"],
                    #reward_config=REWARD_CONFIG,
                    quest_status=quest_dict.get("quest_status", "draft"),
                    quest_name=quest_dict.get("quest_name"),
                    quest_real_goal=quest_dict.get("quest_real_goal"),
                    quest_difficulty=int(quest_dict.get("quest_difficulty")) if quest_dict.get("quest_difficulty") is not None else None,
                    quest_type=quest_dict.get("quest_type"),
                    quest_daily_instances=quest_dict.get("quest_daily_instances", 1),
                    quest_fict_goal=quest_dict.get("quest_fict_goal"),
                    quest_stage=quest_dict.get("quest_stage"),
                    quest_enemy=quest_dict.get("quest_enemy", []),
                    quest_cutscene=quest_dict.get("quest_cutscene"),
                    quest_duration_cat=quest_dict.get("quest_duration_cat"),
                    quest_duration_num=quest_dict.get("quest_duration_num"),
                    quest_duration_weeks=quest_dict.get("quest_duration_weeks"),
                    quest_item_reward=quest_dict.get("quest_item_reward"),
                    quest_creator=quest_dict.get("quest_creator"),
                    quest_participants=quest_dict.get("quest_participants", []),
                    quest_enrolled_users=quest_dict.get("quest_enrolled_users", []),
                    quest_validator=quest_dict.get("quest_validator"),
                    quest_total_users=quest_dict.get("quest_total_users", 0),
                    quest_daily_perfect_count=quest_dict.get("quest_daily_perfect_count"),
                    quest_overall_perfect_count=quest_dict.get("quest_overall_perfect_count"),
                    quest_users_success_count=quest_dict.get("quest_users_success_count"),
                    quest_users_failure_count=quest_dict.get("quest_users_failure_count"),
                    quest_users_unreported_count=quest_dict.get("quest_users_unreported_count"),
                    quest_current_day=quest_dict.get("quest_current_day"),
                    quest_current_instance=quest_dict.get("quest_current_instance"),
                    quest_daily_success_rate=quest_dict.get("quest_daily_success_rate"),
                    quest_overall_success_rate=quest_dict.get("quest_overall_success_rate"),
                    timestamp=quest_dict.get("timestamp")
                )

                quest.update_from_dict(update_data)

                # Perform reward calculations
                xp_reward, gp_reward, honor_reward = quest.calculate_rewards(tier='yellow')
                honor_cost = quest.calculate_cost()

                quest_data[quest_id] = quest.__dict__
                quest_data[quest_id]["Quest_Rewards"] = {
                    "quest_xp_reward": xp_reward,
                    "quest_gp_reward": gp_reward,
                    "quest_honor_reward": honor_reward
                }
                quest_data[quest_id]["Quest_Requirements"] = {
                    "quest_honor_cost": honor_cost,
                    "quest_minimum_enrolled_users": REWARD_CONFIG["default_values"]["quest_minimum_enrolled_users"],
                    "quest_type": REWARD_CONFIG["default_values"]["quest_type"],
                    "quest_minimum_level_requirement": REWARD_CONFIG["difficulty_levels"][str(quest.quest_difficulty)]["quest_minimum_level_requirement"]
                }

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
            update_data[key] = int(value) if key == "quest_difficulty" else value

    return update_data
