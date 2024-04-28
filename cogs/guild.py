import discord
from discord.ext import commands
from discord import app_commands

from datetime import date

from .db import db
from .db import query

class Guild(commands.Cog):
  def __init__(self, bot) -> None:
    self.bot = bot 

  @commands.Cog.listener()
  async def on_raw_thread_update(self, event):
    thread = await self.bot.fetch_channel(event.thread_id)

    await thread.edit(archived=False)
    print(f'Unarchived thread {event.thread_id}')

  @commands.Cog.listener()
  async def on_raw_thread_delete(self, event):
    db.execute(query.GUILD_MEMBER_DELETE, str(event.thread_id))

  @app_commands.command(name="definethreadchannel", description="Sets the channel this command is set in to be the thread channel.")
  async def definethreadchannel(self, interaction: discord.Interaction) -> None:
    db.execute(query.GUILD_THREAD_CHANNEL_INSERT, str(interaction.guild_id), str(interaction.channel_id))

    await interaction.response.send_message("This channel will now be the source for member threads!")

  @app_commands.command(name="addmember", description="Adds a member to the database.")
  @app_commands.default_permissions(manage_roles=True)
  async def addmember(self, interaction: discord.Interaction, member: discord.Member) -> None:
    # Fetch thread channel
    channel = db.fetch(query.GUILD_THREAD_CHANNEL_QUERY, str(interaction.guild_id))
    
    if len(channel) != 1:
      await interaction.response.send_message("You have not set a guild thread channel! Try /definethreadchannel.")
      return

    channel = self.bot.get_channel(int(channel[0][0]))

    # Check if member already has a thread
    memberCheck = db.fetch(query.GUILD_MEMBER_QUERY, str(member.id), str(interaction.guild.id))

    if len(memberCheck) > 0 and memberCheck[0][0] != None:
      await interaction.response.send_message("Member already has a thread!")
      return

    # Create member thread 
    thread = await channel.create_thread(
        name = f"{member.display_name}'s Thread",
        type = discord.ChannelType.private_thread
    )

    db.execute(query.GUILD_MEMBER_INSERT, thread.id, member.id, interaction.guild_id)

    await thread.send(f"Created thread for {member.mention}!")  
    await interaction.response.send_message("Thread created!")

  @app_commands.command(name="documentmiss", description="Document missed hits for a member.")
  @app_commands.default_permissions(manage_roles=True)
  async def documentmiss(self, interaction: discord.Interaction, member: discord.Member, missed: int) -> None:
    # Delete old misses
    db.execute(query.MISSES_DELETE_OLD)

    # Fetch member thread
    thread = db.fetch(query.GUILD_MEMBER_QUERY, str(member.id), str(interaction.guild.id))

    if len(thread) < 1:
      await interaction.response.send_message("Member does not yet have a personal thread!")
      return

    thread = await self.bot.fetch_channel(int(thread[0][0]))

    # Get ID
    id = 0

    max_id = db.fetch(query.MISSES_MAX_ID_QUERY)
    if len(max_id) > 0 and max_id[0][0] != None:
      id = max_id[0][0] + 1

    # Document miss in database
    db.execute(query.MISSES_INSERT, id, str(thread.id), str(interaction.guild.id), missed, str(date.today()))

    # Notify member of misses currently in database from last 30 days
    misses = db.fetch(query.MISSES_QUERY, str(thread.id))

    if len(misses) < 1:
      await interaction.send_message("No misses documented!")
      return
    
    embed = discord.Embed (
      colour = discord.Colour.brand_green(),
      description = f"Misses for {member.mention} in the past 30 days",
      title = f"{member.display_name}'s missed hits"
    )

    missedHits = "\n"
    for miss in misses:
      misses = miss[0]
      missedDate = miss[1]

      missedHits += f"Date: {missedDate} [ Misses: {misses} ]\n"

    embed.add_field(name = "Missed hits:", value = missedHits)
    await thread.send(embed = embed)

    await interaction.response.send_message(f"Documented miss for {member.mention}")

async def setup(bot) -> None:
  await bot.add_cog(Guild(bot))