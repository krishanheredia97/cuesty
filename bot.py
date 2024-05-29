import discord
from discord.ext import commands
from user import User
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
import os
import msg  # Import the msg module

# Load environment variables from .env file
load_dotenv()

# Get the path to the Firebase service account key JSON file from the environment variable
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')

# Initialize Firebase
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cuesty-424dc-default-rtdb.firebaseio.com/'
})

TOKEN = os.getenv('ARMINIO_TOKEN')
VICES_ID = 1238187584434339957  # ID of the 'vices' channel
REWARDS_ID = 1238187584434339956  # ID of the 'rewards' channel
SETTINGS_ID = 1242293048659021886  # ID of the 'settings' channel

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True  # Add this line to enable guild-related events

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
        await assign_default_role(interaction.user)


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
        self.add_item(discord.ui.TextInput(label="Reward Cost", placeholder="Enter the reward cost",
                                           style=discord.TextStyle.short))

    async def on_submit(self, interaction: discord.Interaction):
        reward_name = self.children[0].value.strip()[:30]
        try:
            reward_cost = int(self.children[1].value.strip())
            success, message = self.user.add_reward(reward_name, reward_cost)
        except ValueError:
            success = False
            message = "The cost must be an integer."
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_rewards_buttons(interaction)


class AddRewardButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Add Reward", style=discord.ButtonStyle.green, custom_id="add_reward_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        await interaction.response.send_modal(RewardModal(user))
        user.save_user_data()  # Save updated rewards


class RedeemRewardSelect(discord.ui.Select):
    def __init__(self, user):
        self.user = user
        options = [discord.SelectOption(label=f"{reward['name']} ({reward['cost']}gp)") for reward in
                   self.user.get_unredeemed_rewards()]
        super().__init__(placeholder="Select a reward to redeem", options=options)

    async def callback(self, interaction: discord.Interaction):
        reward_name = self.values[0].split(' (')[0]  # Extract the reward name
        success, message = self.user.redeem_reward(reward_name)
        await interaction.response.send_message(message, ephemeral=True)
        await purge_and_resend_rewards_buttons(interaction)


class RedeemRewardButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Redeem Reward", style=discord.ButtonStyle.danger, custom_id="redeem_reward_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        unredeemed_rewards = user.get_unredeemed_rewards()
        if not unredeemed_rewards:
            await interaction.response.send_message("You have no rewards to redeem.", ephemeral=True)
            return

        view = discord.ui.View(timeout=None)  # Set timeout to None
        view.add_item(RedeemRewardSelect(user))
        await interaction.response.send_message(f"Select a reward to redeem: You have {user.data['gp']}gp available.",
                                                view=view, ephemeral=True)
        user.save_user_data()  # Save updated rewards


class MyRewardsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="My Rewards", style=discord.ButtonStyle.secondary, custom_id="my_rewards_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        user.calculate_rewards()  # Calculate rewards before showing history
        unredeemed_rewards = user.get_unredeemed_rewards()

        embed = discord.Embed(title=f"{user.data['username']}'s Rewards", color=discord.Color.blue())
        if unredeemed_rewards:
            rewards_list = "\n".join([f"{reward['name']} ({reward['cost']}gp)" for reward in unredeemed_rewards])
            embed.add_field(name="Current Rewards", value=rewards_list, inline=False)
        else:
            embed.add_field(name="No rewards to redeem", value=f"You have {user.data['gp']}gp available.", inline=False)

        embed.add_field(name="Available GP", value=f"{user.data['gp']}gp", inline=False)

        await purge_and_resend_rewards_buttons(interaction)
        await interaction.response.send_message(embed=embed, ephemeral=True)
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


class MyVicesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="My Vices", style=discord.ButtonStyle.secondary, custom_id="my_vices_button")

    async def callback(self, interaction: discord.Interaction):
        user = User(str(interaction.user.id), interaction.user.name)
        user.calculate_rewards()  # Calculate rewards before showing vices
        embed = discord.Embed(title=f"{user.data['username']}'s Vices", color=discord.Color.blue())

        for vice in user.data["vices"]:
            status_color = "green" if vice["status"] == "Active" else "red"
            status_text = f"```diff\n+ on withdrawal\n```" if vice[
                                                                  "status"] == "Active" else f"```diff\n- on relapse\n```"
            embed.add_field(name=vice["name"], value=status_text, inline=False)

        await purge_and_resend_vices_buttons(interaction)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        user.save_user_data()  # Save updated rewards


async def purge_and_resend_vices_buttons(interaction):
    channel = interaction.channel
    await channel.purge()
    view = discord.ui.View(timeout=None)  # Set timeout to None
    view.add_item(QuitButton())
    view.add_item(RelapseButton())
    view.add_item(AddViceButton())
    view.add_item(MyVicesButton())
    await channel.send("Click to add, relapse, or view history of vices:", view=view)


async def purge_and_resend_rewards_buttons(interaction):
    channel = interaction.channel
    await channel.purge()
    view = discord.ui.View(timeout=None)  # Set timeout to None
    view.add_item(AddRewardButton())
    view.add_item(RedeemRewardButton())
    view.add_item(MyRewardsButton())
    await channel.send("Click to add or redeem a reward, or view your rewards:", view=view)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    vices_channel = bot.get_channel(VICES_ID)
    rewards_channel = bot.get_channel(REWARDS_ID)
    settings_channel = bot.get_channel(SETTINGS_ID)
    if vices_channel:
        await vices_channel.purge()
        view = discord.ui.View(timeout=None)  # Set timeout to None
        view.add_item(QuitButton())
        view.add_item(RelapseButton())
        view.add_item(AddViceButton())
        view.add_item(MyVicesButton())
        await vices_channel.send("Click to add, relapse, or view history of vices:", view=view)
    if rewards_channel:
        await rewards_channel.purge()
        view = discord.ui.View(timeout=None)  # Set timeout to None
        view.add_item(AddRewardButton())
        view.add_item(RedeemRewardButton())
        view.add_item(MyRewardsButton())
        await rewards_channel.send("Click to add or redeem a reward, or view your rewards:", view=view)
    if settings_channel:
        await settings_channel.send("Use `!setgender <m/f/o>` to set your gender.")

    # Call the send_messages function from msg.py
    await msg.send_messages(bot)


@bot.command(name='setgender')
async def set_gender(ctx, gender):
    if ctx.channel.id != SETTINGS_ID:
        await ctx.send(f"This command can only be used in the settings channel.")
        return

    if gender.lower() not in ['m', 'f', 'o']:
        await ctx.send("Invalid gender. Use `m` for male, `f` for female, and `o` for other.")
        return

    user = User(str(ctx.author.id), ctx.author.name)
    user.data['gender'] = gender.lower()
    user.save_user_data()
    await user.update_role(ctx.author, ctx.guild)  # Ensure role is updated when gender is set
    await ctx.send(f"Gender set to {gender} for {ctx.author.mention}")


@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        user = User(str(after.id), after.name)
        await user.update_role(after, after.guild)


@bot.event
async def on_member_join(member):
    user = User(str(member.id), member.name)
    guild = member.guild
    await user.update_role(member, guild)
    user.save_user_data()


async def assign_default_role(member):
    guild = member.guild
    user = User(str(member.id), member.name)
    await user.update_role(member, guild)


bot.run(TOKEN)
