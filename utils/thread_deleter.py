import os
import discord
from discord.ext import commands

TOKEN2 = os.getenv('TUSK_TOKEN')
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

async def clean_channel(channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel is None:
        print(f"Channel with ID {channel_id} not found.")
        return

    # Delete threads
    threads = channel.threads
    if threads:
        deleted_thread_ids = []
        for thread in threads:
            try:
                await thread.delete()
                deleted_thread_ids.append(thread.id)
            except discord.HTTPException as e:
                print(f"Failed to delete thread {thread.name}: {e}")

        if deleted_thread_ids:
            print(f"Deleted thread IDs: {', '.join(str(id) for id in deleted_thread_ids)}")
        else:
            print("No threads were deleted.")

    # Delete messages
    try:
        deleted = await channel.purge(limit=None)
        print(f"Deleted {len(deleted)} message(s) from channel {channel.name}.")
    except discord.HTTPException as e:
        print(f"Failed to delete messages from channel {channel.name}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    while True:
        channel_id = int(input("Enter the channel ID (0 to exit): "))
        if channel_id == 0:
            break
        await clean_channel(channel_id)
    await bot.close()

bot.run(TOKEN2)