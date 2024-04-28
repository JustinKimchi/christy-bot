import discord
from discord.ext import commands
from discord import app_commands

from .db import db
from .db import query

class Builds(commands.Cog):
  def __init__(self, bot) -> None:
    self.bot = bot
    self.accepted_builds = 1230990420922601594
    self.pending_builds = 1230707906161152070

  @commands.Cog.listener()
  async def on_raw_message_delete(self, event):
    if event.channel_id == self.accepted_builds:
      print('TBD')

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, event):
    # Check if reaction is in pending builds channel
    if event.channel_id == self.pending_builds:
      id_list = db.fetch(query.PENDING_BUILD_MESSAGE_ID_QUERY)
      
      for id in id_list:
        if int(id[0]) == event.message_id:
          # Get info from database of build
          data = db.fetch(query.PENDING_BUILD_QUERY, id[0])
          print(data)

          # Remove from pending builds
          db.execute(query.PENDING_BUILD_DELETE_BY_ID, id[0])

          # Parse data
          name = data[0][0]

          pendingChannel = self.bot.get_channel(event.channel_id)
          pendingMessage = await pendingChannel.fetch_message(event.message_id)

          # Send image into builds channel
          buildsChannel = self.bot.get_channel(self.accepted_builds)
          message = await buildsChannel.send(content=pendingMessage.content)

          # Add pending build to database
          db.execute(query.BUILD_INSERT, name, message.id)
          break

  @app_commands.command(name="requestaddbuild", description="Request to add a build to the database by attaching an image.")
  async def requestaddbuild(self, interaction: discord.Interaction, image: discord.Attachment, name: str) -> None:
    # Check to make sure character name is valid
    alias = name.lower()
    charName = db.fetch(query.BUILD_NAME_QUERY, alias)

    if len(charName) < 1:
      await interaction.response.send_message(f"I don't recognize {name}. Try using the exact name - otherwise, your character may not be in my database yet!")
      return

    # Send message to approval channel
    channel = self.bot.get_channel(self.pending_builds)
    message = await channel.send(content=image)

    # Add to pending builds table
    db.execute(query.PENDING_BUILD_INSERT, charName[0][0], message.id)

    await interaction.response.send_message("Request sent!", ephemeral=True)

  @app_commands.command(name="build", description="Query for a build from the database.")
  async def build(self, interaction: discord.Interaction, name: str):
    # Match name with alias
    foundName = db.fetch(query.BUILD_NAME_QUERY, name.lower())

    if len(foundName) == 0:
      await interaction.response.send_message(f"No character with name {name} found!", ephemeral=True)
      return

    foundName = foundName[0][0]
    parameters = [foundName]

    # Create query for build
    buildquery = query.BUILD_BASE_QUERY
    buildquery += query.BUILD_END_QUERY
    
    # Execute query, respond with results
    build = db.fetchWithTuple(buildquery, tuple(parameters))

    if len(build) == 0 or len(build[0]) == 0:
      await interaction.response.send_message("No builds for this character yet!", ephemeral=True)  

    # Send the build in channel
    channel = self.bot.get_channel(self.accepted_builds)
    message = await channel.fetch_message(int(build[0][0]))

    embed = discord.Embed (
      colour = discord.Colour.brand_green(),
      description="Here's a random build from my database!",
      title=foundName
    )

    embed.set_image(url=message.content)

    await interaction.response.send_message(embed=embed)

  @app_commands.command(name="addname", description="Add a name to the database.")
  @app_commands.default_permissions(manage_roles=True)
  async def addname(self, interaction: discord.Interaction, name: str):
    # Check if database already has a name
    foundName = db.fetch(query.BUILD_NAME_QUERY, name.lower())

    if len(foundName) != 0:
      await interaction.response.send_message(f"{foundName[0][0]} is already in the database!", ephemeral=True)
      return
    
    db.execute(query.BUILD_NAME_INSERT, name.lower(), name)

  @app_commands.command(name="addalias", description="Add an alias to the database paired with a name.")
  @app_commands.default_permissions(manage_roles=True)
  async def addalias(self, interaction: discord.Interaction, name: str, alias: str):
    # Check if database already has an alias
    foundName = db.fetch(query.BUILD_NAME_QUERY, name.lower())

    if len(foundName) != 0:
      await interaction.response.send_message(f"{foundName[0][0]} is already in the database!", ephemeral=True)
      return

    db.execute(query.BUILD_NAME_INSERT, alias.lower(), name)

async def setup(bot) -> None:
  await bot.add_cog(Builds(bot))