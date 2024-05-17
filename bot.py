# bot.py

import discord
from discord.ext import commands
import data_manager
from user import User
import os

TOKEN = os.getenv('Cuesty_Discord_Bot')
VICES_ID = 1238187584434339957  # ID of the 'vices' channel
REWARDS_ID = 1238187584434339956  # ID of the 'rewards' channel

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

class ViceModal(discord.ui.Modal):
    def __init__(self, user):
        super().__init__(title="Add a New Vice")
        self.user = user
        self.add_item(discord.ui.TextInput(label="Vice Name", placeholder="Enter the vice you want to manage"))

    async def on_submit(self, interaction: discord.Interaction):
        vice_name = self.children[0].value.strip()[:30]
        success, message = self.user.add_vice(vice_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_vices_buttons(interaction)

class AddViceButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Add Vice", style=discord.ButtonStyle.blurple, custom_id="add_vice_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        user.calculate_rewards()  # Calculate rewards before adding a new vice
        await interaction.response.send_modal(ViceModal(user))
        user.save_user_data()  # Save updated rewards

class RewardModal(discord.ui.Modal):
    def __init__(self, user):
        super().__init__(title="Add a New Reward")
        self.user = user
        self.add_item(discord.ui.TextInput(label="Reward Name", placeholder="Enter the reward name"))

    async def on_submit(self, interaction: discord.Interaction):
        reward_name = self.children[0].value.strip()[:30]
        success, message = self.user.add_reward(reward_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_rewards_buttons(interaction)

class AddRewardButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Add Reward", style=discord.ButtonStyle.green, custom_id="add_reward_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        await interaction.response.send_modal(RewardModal(user))
        user.save_user_data()  # Save updated rewards

class RelapseSelect(discord.ui.Select):
    def __init__(self, user):
        self.user = user
        options = [discord.SelectOption(label=vice) for vice in self.user.get_active_vices()]
        super().__init__(placeholder="Select a vice to mark as relapsed", options=options)

    async def callback(self, interaction: discord.Interaction):
        vice_name = self.values[0]
        success, message = self.user.relapse_vice(vice_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_vices_buttons(interaction)

class RelapseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Relapse", style=discord.ButtonStyle.danger, custom_id="relapse_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        user.calculate_rewards()  # Calculate rewards before relapsing a vice
        active_vices = user.get_active_vices()
        if not active_vices:
            await interaction.response.send_message("You have no active vices.", ephemeral=True)
            return

        view = discord.ui.View(timeout=None)  # Set timeout to None
        view.add_item(RelapseSelect(user))
        await interaction.response.send_message("Select a vice to mark as relapsed:", view=view, ephemeral=True)
        user.save_user_data()  # Save updated rewards

class QuitSelect(discord.ui.Select):
    def __init__(self, user):
        self.user = user
        options = [discord.SelectOption(label=vice) for vice in self.user.get_inactive_vices()]
        super().__init__(placeholder="Select a vice to mark as active", options=options)

    async def callback(self, interaction: discord.Interaction):
        vice_name = self.values[0]
        success, message = self.user.quit_vice(vice_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_vices_buttons(interaction)

class QuitButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Quit", style=discord.ButtonStyle.green, custom_id="quit_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        user.calculate_rewards()  # Calculate rewards before quitting a vice
        inactive_vices = user.get_inactive_vices()
        if not inactive_vices:
            await interaction.response.send_message("You have no inactive vices.", ephemeral=True)
            return

        view = discord.ui.View(timeout=None)  # Set timeout to None
        view.add_item(QuitSelect(user))
        await interaction.response.send_message("Select a vice to mark as active:", view=view, ephemeral=True)
        user.save_user_data()  # Save updated rewards

class UserHistoryButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Show History", style=discord.ButtonStyle.secondary, custom_id="history_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        user.calculate_rewards()  # Calculate rewards before showing history
        embed = discord.Embed(title=f"{user.data['username']}'s Vice History", color=discord.Color.blue())

        for vice in user.data["vices"]:
            vice_log = ""
            for log_entry in vice["log"]:
                vice_log += f"{log_entry['action'].capitalize()} on {log_entry['timestamp']}\n"
            embed.add_field(name=vice["name"], value=vice_log or "No actions recorded.", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        user.save_user_data()  # Save updated rewards

async def purge_and_resend_vices_buttons(interaction):
    channel = interaction.channel
    await channel.purge()
    view = discord.ui.View(timeout=None)  # Set timeout to None
    view.add_item(QuitButton())
    view.add_item(RelapseButton())
    view.add_item(AddViceButton())
    view.add_item(UserHistoryButton())
    await channel.send("Click to add, relapse, or view history of vices:", view=view)

async def purge_and_resend_rewards_buttons(interaction):
    channel = interaction.channel
    await channel.purge()
    view = discord.ui.View(timeout=None)  # Set timeout to None
    view.add_item(AddRewardButton())
    await channel.send("Click to add a reward:", view=view)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    vices_channel = bot.get_channel(VICES_ID)
    rewards_channel = bot.get_channel(REWARDS_ID)
    if vices_channel:
        await vices_channel.purge()
        view = discord.ui.View(timeout=None)  # Set timeout to None
        view.add_item(QuitButton())
        view.add_item(RelapseButton())
        view.add_item(AddViceButton())
        view.add_item(UserHistoryButton())
        await vices_channel.send("Click to add, relapse, or view history of vices:", view=view)
    if rewards_channel:
        await rewards_channel.purge()
        view = discord.ui.View(timeout=None)  # Set timeout to None
        view.add_item(AddRewardButton())
        await rewards_channel.send("Click to add a reward:", view=view)

bot.run(TOKEN)
