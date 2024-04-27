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

  async def on_ready(self):
    print("Bot is online")

bot = ChristyBot()

@bot.command()
async def sync(ctx):
  print("sync command")
  if ctx.author.id == 277851099850080258:
    print('syncing')
    await bot.tree.sync()
    await ctx.send('Command tree synced.')
  else:
    await ctx.send('You must be the owner to use this command!')

bot.run(token)