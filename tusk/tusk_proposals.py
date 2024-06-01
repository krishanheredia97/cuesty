# tusk_proposals.py
import discord
from discord.ext import commands
import os
import random
import string
from datetime import datetime, timezone, timedelta
import json
from dotenv import load_dotenv
from quest_class import Quest
from quest_data_manager import load_quest_data, save_quest_data
from d_msg_summary_quest import generate_summary
from tusk_accepted_quests import handle_accepted_quest


load_dotenv()

TOKEN2 = os.getenv('TUSK_TOKEN')
CREATE_QUEST_CHANNEL_ID = 1243061918080438272
THREADS_CHANNEL_ID = 1243061918080438272

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

with open('quest_default_config.json', 'r') as file:
    QUEST_DEFAULT_CONFIG = json.load(file)

def generate_unique_id(length=5):
    # Function to generate a unique ID
    return ''.join(random.choices(string.ascii_uppercase, k=length))

class CreateQuestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Create Quest", style=discord.ButtonStyle.blurple, custom_id="create_quest_button")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        thread_name = f"Q - {generate_unique_id()}"
        threads_channel = bot.get_channel(THREADS_CHANNEL_ID)

        if not isinstance(threads_channel, discord.TextChannel):
            await interaction.followup.send("The configured channel for creating threads is not a text channel.", ephemeral=True)
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
                    "quest_creator": creator.name,
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
                    "quest_minimum_enrolled_users": QUEST_DEFAULT_CONFIG["default_values"]["quest_minimum_enrolled_users"],
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

        await thread.send(f"Ah, {creator.mention}, I see you want to arrange a new quest. Let's get started with the details, shall we?\n\nFirst, what do you want the mission to be called, sir?")
        await ask_name(thread, creator, quest_id)

async def ask_name(thread, creator, quest_id):
    def check(m):
        return m.channel == thread and m.author == creator

    message = await bot.wait_for('message', check=check)
    name = message.content.capitalize()

    quest_data = load_quest_data()
    quest_data[quest_id]["Quest_Main"].update({"quest_name": name})
    save_quest_data(quest_data)

    await thread.send(f"Understood, sir. Now, what is the specific real-life challenge or task that needs to be achieved during this quest?")
    await ask_challenge(thread, creator, quest_id)

async def ask_challenge(thread, creator, quest_id):
    def check(m):
        return m.channel == thread and m.author == creator

    message = await bot.wait_for('message', check=check)
    challenge = message.content.capitalize()

    quest_data = load_quest_data()
    quest_data[quest_id]["Quest_Main"].update({"quest_real_goal": challenge})
    save_quest_data(quest_data)

    await thread.send(f"Understood, sir. What will be our mission, the fictional goal of this quest?")
    await ask_mission(thread, creator, quest_id)

async def ask_mission(thread, creator, quest_id):
    def check(m):
        return m.channel == thread and m.author == creator

    message = await bot.wait_for('message', check=check)
    mission = message.content.capitalize()

    quest_data = load_quest_data()
    quest_data[quest_id]["Quest_Narrative"].update({"quest_fict_goal": mission})
    save_quest_data(quest_data)

    await thread.send("Understood, sir. Please provide a brief narrative introduction that gives context and background about the quest.")
    await ask_intro(thread, creator, quest_id)

async def ask_intro(thread, creator, quest_id):
    def check(m):
        return m.channel == thread and m.author == creator

    message = await bot.wait_for('message', check=check)
    intro = message.content.capitalize()

    quest_data = load_quest_data()
    quest_data[quest_id]["Quest_Narrative"].update({"quest_cutscene": intro})
    save_quest_data(quest_data)

    await thread.send(f"Understood, sir. Now, please provide descriptions of the quest environment to enhance the narrative.")
    await ask_stage_descriptions(thread, creator, quest_id)

async def ask_stage_descriptions(thread, creator, quest_id):
    def check(m):
        return m.channel == thread and m.author == creator

    message = await bot.wait_for('message', check=check)
    stage_descriptions = message.content.capitalize()

    quest_data = load_quest_data()
    quest_data[quest_id]["Quest_Narrative"].update({"quest_stage": stage_descriptions})
    save_quest_data(quest_data)

    await thread.send(f"Understood, sir. Let's set the duration for the quest.")
    await ask_duration_cat(thread, creator, quest_id)

class DurationButton(discord.ui.Button):
    def __init__(self, label, duration):
        super().__init__(label=label, style=discord.ButtonStyle.primary if duration == 'w' else discord.ButtonStyle.success if duration == 'm' else discord.ButtonStyle.danger)
        self.duration = duration

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        thread = interaction.channel
        creator = interaction.user
        quest_id = str(thread.id)

        quest_data = load_quest_data()
        quest_data[quest_id]["Quest_Time"].update({"quest_duration_cat": self.duration})
        save_quest_data(quest_data)

        duration_word = "weeks" if self.duration == 'w' else "months" if self.duration == 'm' else "years"
        await thread.send(f"Now, how many {duration_word} will the mission take?")
        await ask_duration_num(thread, creator, quest_id, duration_word)

async def ask_duration_cat(thread, creator, quest_id):
    view = discord.ui.View()
    view.add_item(DurationButton("Weeks", 'w'))
    view.add_item(DurationButton("Months", 'm'))
    view.add_item(DurationButton("Years", 'y'))

    await thread.send("Sir, how long do you think the mission will take?", view=view)

async def ask_duration_num(thread, creator, quest_id, duration_word):
    def check(m):
        return m.channel == thread and m.author == creator and m.content.isdigit()

    message = await bot.wait_for('message', check=check)
    duration_num = int(message.content)
    duration_weeks = duration_num if duration_word == 'weeks' else duration_num * 4 if duration_word == 'months' else duration_num * 52

    quest_data = load_quest_data()
    quest_start_date = datetime.now().date()
    quest_end_date = quest_start_date + timedelta(weeks=duration_weeks)

    quest_data[quest_id]["Quest_Time"].update({
        "quest_duration_num": duration_num,
        "quest_duration_weeks": duration_weeks,
        "quest_start_date": str(quest_start_date),
        "quest_end_date": str(quest_end_date)
    })
    save_quest_data(quest_data)

    await thread.send(f"Understood, sir. What type of enemies shall we expect on our mission?")
    await ask_enemy(thread, creator, quest_id)

async def ask_enemy(thread, creator, quest_id):
    def check(m):
        return m.channel == thread and m.author == creator

    message = await bot.wait_for('message', check=check)
    enemy = message.content.capitalize()

    quest_data = load_quest_data()
    quest_data[quest_id]["Quest_Narrative"].update({"quest_enemy": enemy})
    save_quest_data(quest_data)

    await thread.send(f"Understood, sir. Finally, what is the level of difficulty of the quest, from 1 to 4?")
    await ask_difficulty(thread, creator, quest_id)

async def ask_difficulty(thread, creator, quest_id):
    def check(m):
        return m.channel == thread and m.author == creator and m.content.isdigit() and 1 <= int(m.content) <= 4

    message = await bot.wait_for('message', check=check)
    difficulty = int(message.content)

    quest_data = load_quest_data()
    quest_data[quest_id]["Quest_Main"].update({"quest_difficulty": difficulty})

    quest = Quest(
        quest_id=quest_id,
        quest_name=quest_data[quest_id]["Quest_Main"]["quest_name"],
        quest_real_goal=quest_data[quest_id]["Quest_Main"]["quest_real_goal"],
        quest_fict_goal=quest_data[quest_id]["Quest_Narrative"]["quest_fict_goal"],
        quest_cutscene=quest_data[quest_id]["Quest_Narrative"]["quest_cutscene"],
        quest_stage=quest_data[quest_id]["Quest_Narrative"]["quest_stage"],
        quest_item_reward=None,  # Set to None by default
        quest_duration_weeks=quest_data[quest_id]["Quest_Time"]["quest_duration_weeks"],
        quest_enemy=quest_data[quest_id]["Quest_Narrative"]["quest_enemy"],
        quest_difficulty=quest_data[quest_id]["Quest_Main"]["quest_difficulty"],
        reward_config=QUEST_DEFAULT_CONFIG
    )

    xp_reward, gp_reward, honor_reward = quest.calculate_rewards(tier='yellow')
    honor_cost = quest.calculate_cost()

    quest_data[quest_id]["Quest_Rewards"].update({
        "quest_xp_reward": xp_reward,
        "quest_gp_reward": gp_reward,
        "quest_honor_reward": honor_reward
    })

    quest_data[quest_id]["Quest_Requirements"].update({
        "quest_honor_cost": honor_cost,
        "quest_minimum_enrolled_users": QUEST_DEFAULT_CONFIG["default_values"]["quest_minimum_enrolled_users"],
        "quest_type": QUEST_DEFAULT_CONFIG["default_values"]["quest_type"],
        "quest_minimum_level_requirement": QUEST_DEFAULT_CONFIG["difficulty_levels"][str(difficulty)]["quest_minimum_level_requirement"]
    })
    save_quest_data(quest_data)

    summary = generate_summary(quest, xp_reward, gp_reward, honor_reward, honor_cost)

    await thread.send(summary)

    view = ReviewView(quest_id)
    await thread.send("Please review the quest details above. If everything is correct, click the button below to send it to review, restart to make changes, or delete the quest.", view=view)

class ReviewView(discord.ui.View):
    def __init__(self, quest_id):
        super().__init__(timeout=None)
        self.quest_id = quest_id
        self.add_item(SendToReviewButton(quest_id))
        self.add_item(RestartButton(quest_id))
        self.add_item(DeleteButton(quest_id))
class AcceptButton(discord.ui.Button):
    def __init__(self, quest_id):
        super().__init__(label="Accept", style=discord.ButtonStyle.success, custom_id=f"accept_{quest_id}")
        self.quest_id = quest_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        quest_data = load_quest_data()

        if self.quest_id in quest_data:
            quest_data[self.quest_id]["Quest_Main"]["quest_status"] = "accepted"
            save_quest_data(quest_data)

            # Trigger the quest handling actions
            guild = interaction.guild
            await handle_accepted_quest(guild, self.quest_id)

        await interaction.followup.send("Quest has been accepted and the quest setup process has started.", ephemeral=True)

class DeniedButton(discord.ui.Button):
    def __init__(self, quest_id):
        super().__init__(label="Denied", style=discord.ButtonStyle.danger, custom_id=f"denied_{quest_id}")
        self.quest_id = quest_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        quest_data = load_quest_data()

        if self.quest_id in quest_data:
            quest_data[self.quest_id]["Quest_Main"]["quest_status"] = "denied"
            save_quest_data(quest_data)

        await interaction.followup.send("Quest has been denied.", ephemeral=True)


class ReviewActionsView(discord.ui.View):
    def __init__(self, quest_id):
        super().__init__(timeout=None)
        self.quest_id = quest_id
        self.add_item(AcceptButton(quest_id))
        self.add_item(DeniedButton(quest_id))


class SendToReviewButton(discord.ui.Button):
    def __init__(self, quest_id):
        super().__init__(label="Send to Review", style=discord.ButtonStyle.blurple, custom_id=f"send_to_review_{quest_id}")
        self.quest_id = quest_id

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
            reward_config=QUEST_DEFAULT_CONFIG
        )

        summary = generate_summary(
            quest,
            quest_dict["Quest_Rewards"]["quest_xp_reward"],
            quest_dict["Quest_Rewards"]["quest_gp_reward"],
            quest_dict["Quest_Rewards"]["quest_honor_reward"],
            quest_dict["Quest_Requirements"]["quest_honor_cost"]
        )

        review_channel_id = 1245264665315901460
        review_channel = bot.get_channel(review_channel_id)

        if not isinstance(review_channel, discord.TextChannel):
            await interaction.followup.send("The configured review channel is not a text channel.", ephemeral=True)
            return

        thread_name = f"Review - {quest.quest_name}"
        review_thread = await review_channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)

        await review_thread.send(summary, view=ReviewActionsView(self.quest_id))
        await interaction.followup.send("Quest sent to review and summary posted in the review channel.", ephemeral=True)

class RestartButton(discord.ui.Button):
    def __init__(self, quest_id):
        super().__init__(label="Restart", style=discord.ButtonStyle.gray, custom_id=f"restart_{quest_id}")
        self.quest_id = quest_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        thread = interaction.channel
        creator = interaction.user

        await thread.send(f"Ah, {creator.mention}, let's restart the quest creation process. What do you want the mission to be called, sir?")
        await ask_name(thread, creator, self.quest_id)

class DeleteButton(discord.ui.Button):
    def __init__(self, quest_id):
        super().__init__(label="Delete", style=discord.ButtonStyle.danger, custom_id=f"delete_{quest_id}")
        self.quest_id = quest_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        quest_data = load_quest_data()

        if self.quest_id in quest_data:
            del quest_data[self.quest_id]
            save_quest_data(quest_data)

        thread = interaction.channel
        await thread.delete()

class CreateQuestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CreateQuestButton())
