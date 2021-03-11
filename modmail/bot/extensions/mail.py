import discord
from discord.ext import commands

import modmail


class Mail(commands.Cog):
    def __init__(self, bot: modmail.bot.Bot) -> None:
        self.bot = bot


def setup(bot: modmail.bot.Bot) -> None:
    bot.add_cog(Mail(bot))
