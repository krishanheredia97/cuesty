import discord
from discord.ext import commands
from discord.ui import Button, View

class AddRewardButton(Button):
    def __init__(self):
        super().__init__(label="Add Reward", style=discord.ButtonStyle.green, custom_id="dummy_add_reward")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction silently


class RedeemRewardButton(Button):
    def __init__(self):
        super().__init__(label="Redeem Reward", style=discord.ButtonStyle.danger, custom_id="dummy_redeem_reward")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction silently


class MyRewardsButton(Button):
    def __init__(self):
        super().__init__(label="My Rewards", style=discord.ButtonStyle.secondary, custom_id="dummy_my_rewards")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction silently


class AddViceButton(Button):
    def __init__(self):
        super().__init__(label="Add Vice", style=discord.ButtonStyle.blurple, custom_id="dummy_add_vice")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction silently


class RelapseButton(Button):
    def __init__(self):
        super().__init__(label="Relapse", style=discord.ButtonStyle.red, custom_id="dummy_relapse")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction silently


class QuitButton(Button):
    def __init__(self):
        super().__init__(label="Quit", style=discord.ButtonStyle.green, custom_id="dummy_quit")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction silently


class MyVicesButton(Button):
    def __init__(self):
        super().__init__(label="My Vices", style=discord.ButtonStyle.gray, custom_id="dummy_my_vices")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction silently


async def send_messages(bot):
    rewards_channel_id = 1242961708947865681
    vices_channel_id = 1242972352577405040

    rewards_channel = bot.get_channel(rewards_channel_id)
    vices_channel = bot.get_channel(vices_channel_id)

    if rewards_channel:
        await rewards_channel.purge()  # Purge the channel before sending new messages

        # Message 1
        message_content_1 = """
# What are Rewards?

Rewards are incentives you give to yourself for maintaining good habits. For example, you might reward yourself with an ice cream every week you spend without smoking. When you add a reward, you need to give it a name and assign a value in GP (the server's currency), which you earn by abstaining from vices.

## Steps to Administer Your Rewards

### Step 1
Determine how much GP your reward will cost (check <#1242954833569382452> for picking a reward category or <#1242958133769404466> for calculating a custom reward cost).

### Step 2
Go to the channel <#1238187584434339956> for administering rewards.
"""
        await rewards_channel.send(message_content_1)

        # Message 2 with Add Reward button
        message_content_2 = """
### Step 3
Use this button to add a new reward.
"""
        view_1 = View()
        view_1.add_item(AddRewardButton())
        await rewards_channel.send(message_content_2, view=view_1)

        # Message 3 with Redeem Reward button
        message_content_3 = """
### Step 4
Use this button to redeem a reward using your earned GP.
"""
        view_2 = View()
        view_2.add_item(RedeemRewardButton())
        await rewards_channel.send(message_content_3, view=view_2)

        # Message 4 with My Rewards button
        message_content_4 = """
### My Rewards
Use this button to view your available GP and rewards.
"""
        view_3 = View()
        view_3.add_item(MyRewardsButton())
        await rewards_channel.send(message_content_4, view=view_3)

    if vices_channel:
        await vices_channel.purge()  # Purge the channel before sending new messages

        # Message 1
        message_content_5 = """
# What are Vices?

Vices are habits or behaviors that you are trying to quit or manage. Our server focuses on tracking vices instead of "good habits" because it is easier to manage abstinence from bad habits than constant instances of successfully doing good habits. In the future, the server will include functionality for administering good habits as well.

## Steps to Manage Your Vices

### Step 1
Go to the channel <#1238187584434339957> for administering vices.
"""
        await vices_channel.send(message_content_5)

        # Message 2 with Add Vice button
        message_content_6 = """
### Step 2
Add a new vice by using the button below.
"""
        view_4 = View()
        view_4.add_item(AddViceButton())
        await vices_channel.send(message_content_6, view=view_4)

        # Message 3 with Relapse button
        message_content_7 = """
### Step 3
Register a relapse as soon as it occurs using the button below.
"""
        view_5 = View()
        view_5.add_item(RelapseButton())
        await vices_channel.send(message_content_7, view=view_5)

        # Message 4 with Quit button
        message_content_8 = """
### Step 4
Quit an existing habit after a relapse using the button below.
"""
        view_6 = View()
        view_6.add_item(QuitButton())
        await vices_channel.send(message_content_8, view=view_6)

        # Message 5 with My Vices button
        message_content_9 = """
### My Vices
Use this button to view your current and past vices.
"""
        view_7 = View()
        view_7.add_item(MyVicesButton())
        await vices_channel.send(message_content_9, view=view_7)

    else:
        print(f"Channel with ID {vices_channel_id} not found.")
