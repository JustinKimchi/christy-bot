import discord
from discord.ext import commands
from discord import app_commands

from .db import db
from .db import query

class Roles(commands.Cog):
  def __init__(self, bot) -> None:
    self.bot = bot

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, event):
    # Fetch reaction channels
    idx = db.fetch(query.REACTION_CHANNEL_ID_QUERY, str(event.message_id))

    if (len(idx) < 1):
      return
    
    # Get message ids
    idx = idx[0][0]

    # Check to see if reaction was on role react message
    if not str(event.message_id) in idx:
      return

    # Get the guild id
    guild_id = str(event.guild_id)
    guild = discord.utils.find(lambda g: g.id == event.guild_id, self.bot.guilds)

    # Fetch appropriate role reactions
    rrs = db.fetch(query.REACTION_ROLE_EMOJI_QUERY, guild_id)

    # Check to see if reaction is in list of role reactions for the server
    for rr in rrs:
      if str(event.emoji) == rr[0]:
        role = discord.utils.get(guild.roles, name=rr[1])

        if role is not None:
          member = discord.utils.find(lambda m: m.id == event.user_id, guild.members)

          if member is not None:
            await member.add_roles(role)

            print(f"Added role {role} for user {member}.")

  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, event):
    # Fetch reaction channels
    idx = db.fetch(query.REACTION_CHANNEL_ID_QUERY, str(event.message_id))

    if (len(idx) < 1):
      return
    
    # Get message ids
    idx = idx[0][0]

    # Check to see if reaction was on role react message
    if not str(event.message_id) in idx:
      return

    # Get the guild id
    guild_id = str(event.guild_id)
    guild = discord.utils.find(lambda g: g.id == event.guild_id, self.bot.guilds)

    # Fetch appropriate role reactions
    rrs = db.fetch(query.REACTION_ROLE_EMOJI_QUERY, guild_id)

    # Check to see if reaction is in list of role reactions for the server
    for rr in rrs:
      if str(event.emoji) == rr[0]:
        role = discord.utils.get(guild.roles, name=rr[1])

        if role is not None:
          member = discord.utils.find(lambda m: m.id == event.user_id, guild.members)

          if member is not None:
            
            await member.remove_roles(role)
            print(f"Removed role {role} for user {member}.")

  @app_commands.command(name="setrolemessage", description="Sets up role reaction message for the server.")
  async def setrolemessage(self, interaction: discord.Interaction, channel_id: str, message_id: str) -> None:
    guild_id = interaction.guild_id

    # Update database for role channel/message
    db.execute(query.REACTION_INSERT_CHANNEL, guild_id, channel_id, message_id)
    db.execute(query.REACTION_UPDATE_CHANNEL, channel_id, guild_id)
    db.execute(query.REACTION_UDPATE_MESSAGE, message_id, guild_id)

    # Delete previous reaction roles
    db.execute(query.REACTION_DELETE_CHANNEL, str(guild_id))

    await interaction.response.send_message("Role message set!")

  @app_commands.command(name="addreactionrole", description="Add a reaction + role pairing for role reaction.")
  async def addreactionrole(self, interaction: discord.Interaction, emoji: str, role: str) -> None:
    guild_id = interaction.guild_id

    # Add reaction to reaction message
    data = db.fetch(query.REACTION_CHANNEL_QUERY, str(guild_id))

    if len(data) < 1:
      # If reaction role message has not been set, return
      await interaction.response.send_message("Set a role message before adding reaction roles!")
      return

    # Check if emoji has already been used
    edata = db.fetch(query.REACTION_EMOJI_QUERY, emoji)

    if len(edata) > 0:
      await interaction.response.send_message("Emoji has already been used")
      return

    channel_id = data[0][0]
    message_id = data[0][1]

    channel = self.bot.get_channel(int(channel_id))
    if not channel == None:
      message = await discord.utils.get(channel.history(), id=int(message_id))

      if not message == None:
        found = False
        for e in interaction.guild.emojis:
          if str(e) == str(emoji):
            found = True

        if found or discord.PartialEmoji.from_str(emoji).is_unicode_emoji():
          await message.add_reaction(emoji)
        else:
          await interaction.response.send_message("Please select an emoji in the server.")
          return

    # Update database for reaction role
    id = db.fetch(query.REACTION_MAX_ID_QUERY)[0][0] + 1
    db.execute(query.REACTION_INSERT_RR, id, emoji, role, guild_id)

    await interaction.response.send_message("Reaction role added!")

  @app_commands.command(name="removereactionrole", description="Remove a reaction + role pairing for role reaction.")
  async def removereactionrole(self, interaction: discord.Interaction, emoji: str) -> None:
    guild_id = interaction.guild_id

    # Remove reaction from reaction message
    data = db.fetch(query.REACTION_CHANNEL_QUERY, str(guild_id))

    if len(data) < 1:
      # If reaction role message has not been set, return
      await interaction.response.send_message("Role message not set!")
      return

    # Check if emoji is in reaction roles
    edata = db.fetch(query.REACTION_EMOJI_QUERY, emoji)

    if len(edata) < 1:
      await interaction.response.send_message("Emoji is not a reaction role emoji!")
      return

    channel_id = data[0][0]
    message_id = data[0][1]

    channel = self.bot.get_channel(int(channel_id))
    if not channel == None:
      message = await discord.utils.get(channel.history(), id=int(message_id))

      if not message == None:
        found = False
        for e in interaction.guild.emojis:
          if str(e) == str(emoji):
            found = True

        if found or discord.PartialEmoji.from_str(emoji).is_unicode_emoji():
          await message.remove_reaction(emoji, self.bot.user)
        else:
          await interaction.response.send_message("Not a reaction role emoji!")
          return

    # Update database for reaction role
    db.execute(query.REACTION_DELETE_RR, emoji)

    await interaction.response.send_message("Reaction role removed!")

async def setup(bot) -> None:
  await bot.add_cog(Roles(bot))