import discord
from discord.ext import commands

import modmail


class Mail(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot: modmail.bot.Bot) -> None:
        self.bot = bot

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return


def setup(bot: modmail.bot.Bot) -> None:
    bot.add_cog(Mail(bot))
