import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

class ChristyBot(commands.Bot):
  def __init__(self):
    super().__init__(command_prefix = "?", intents = discord.Intents.all())

  async def setup_hook(self):
    for filename in os.listdir("./cogs"):
      if filename.endswith(".py"):
        await self.load_extension(f"cogs.{filename[:-3]}")

    await bot.tree.sync()

  async def on_ready(self):
    print("Bot is online")

bot = ChristyBot()
bot.run(token)