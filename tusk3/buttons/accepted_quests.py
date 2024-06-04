import discord
from discord.ui import View
from datetime import datetime
from arminio.data_manager import load_quest_data, save_quest_data

CATEGORY_ID_TO_DUPLICATE = 1245263224480202883
CHANNELS_TO_DUPLICATE = {
    1245372881014100099: '🟡│task-check-in',
    1245263225751339088: '📜│quest-info',
    1245371676334489610: '🐎│battlefield',
    1245371990731264010: '🔥│bonfire'
}
BOT_ROLE_ID = 1245506986834001992


async def handle_accepted_quest(bot, guild, quest_id):
    # Fetch the bot's member object
    bot_member = guild.get_member(bot.user.id)
    if not bot_member:
        return

    # Check initial permissions
    permissions = bot_member.guild_permissions
    if permissions.manage_channels and permissions.manage_roles:
        try:
            # Create a new role
            new_role = await guild.create_role(name=f'Role for Quest {quest_id}')
            print(f"Created role ID: {new_role.id}")

            # Fetch the category to duplicate
            original_category = guild.get_channel(CATEGORY_ID_TO_DUPLICATE)
            if not original_category or not isinstance(original_category, discord.CategoryChannel):
                return

            # Duplicate the category with its permissions and rename it
            new_category = await guild.create_category(
                name=f'Quest {quest_id} Category',
                overwrites=original_category.overwrites
            )

            # List to hold all new channel IDs
            new_channel_ids = [new_category.id]

            # Duplicate each specified channel inside the new category with the new name
            for original_channel_id, new_channel_name in CHANNELS_TO_DUPLICATE.items():
                original_channel = guild.get_channel(original_channel_id)
                if original_channel and isinstance(original_channel, discord.TextChannel):
                    new_channel = await new_category.create_text_channel(
                        name=new_channel_name,
                        overwrites=original_channel.overwrites,
                        topic=original_channel.topic,
                        nsfw=original_channel.nsfw,
                        slowmode_delay=original_channel.slowmode_delay
                    )
                    new_channel_ids.append(new_channel.id)

                    # Send buttons to the '🟡│task-check-in' channel
                    if new_channel_name == '🟡│task-check-in':
                        await send_task_check_in_buttons(new_channel)

            # Print the list of new channel IDs
            print(f"Created category and channel IDs: {new_channel_ids}")

        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass


# Function to send task check-in buttons
async def send_task_check_in_buttons(channel):
    class TaskCheckInView(View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
        async def yes_button_callback(self, interaction, button):
            await update_user_progress(interaction.user.id, 'yes')
            await interaction.response.send_message("You clicked Yes!", ephemeral=True)

        @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
        async def no_button_callback(self, interaction, button):
            await update_user_progress(interaction.user.id, 'no')
            await interaction.response.send_message("You clicked No!", ephemeral=True)

    view = TaskCheckInView()
    await channel.send("Did you complete your task today?", view=view)


async def update_user_progress(user_id, response):
    data = load_quest_data(user_id)
    if 'Quest_Main' not in data:
        data['Quest_Main'] = {'quest_id': user_id}

    if 'quest_individual_progress' not in data:
        data['quest_individual_progress'] = {
            'quest_individual_success_log': {'count': 0, 'timestamps': []},
            'quest_individual_failure_log': {'count': 0, 'timestamps': []}
        }

    timestamp = datetime.utcnow().isoformat()
    if response == 'yes':
        data['quest_individual_progress']['quest_individual_success_log']['count'] += 1
        data['quest_individual_progress']['quest_individual_success_log']['timestamps'].append(timestamp)
    else:
        data['quest_individual_progress']['quest_individual_failure_log']['count'] += 1
        data['quest_individual_progress']['quest_individual_failure_log']['timestamps'].append(timestamp)

    save_quest_data(data)
