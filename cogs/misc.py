import discord
from discord.ext import commands
from discord import app_commands

import random

class Misc(commands.Cog):
  def __init__(self, bot) -> None:
    self.bot = bot 

  @app_commands.command(name="8ball", description="Ask the magic 8ball a question!")
  async def _8ball(self, interaction: discord.Interaction, question: str) -> None:
    responses = ['It is certain.',
                'It is decidedly so.',
                'Without a doubt.',
                'Yes - definitely.',
                'You may rely on it.',
                'As I see it, yes.',
                'Most likely.',
                'Outlook good.',
                'Yes.',
                'Signs point to yes.',
                'Reply hazy, try again.',
                'Ask again later.',
                'Better not tell you now.',
                'Cannot predict now.',
                'Concentrate and ask again.',
                "Don't count on it.",
                'My reply is no.',
                'My sources say no.',
                'Outlook not so good',
                'Very doubtful']

    embed = discord.Embed(
      title = "Magic 8 Ball",
      description = "Ask the magic 8 ball a question!"
    )

    embed.add_field(name = "Question:", value = question)
    embed.add_field(name = "Answer:", value = random.choice(responses))

    #embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1072673373001355359/1072679485889056818/Chloe.png")

    await interaction.response.send_message(embed = embed)

async def setup(bot) -> None:
  await bot.add_cog(Misc(bot))