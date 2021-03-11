import discord
from discord.ext import commands

import modmail
from modmail import Config


class Hub(commands.Cog):
    __slots__ = ("bot", "guild", "commands", "stdout")

    def __init__(self, bot: modmail.bot.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.guild = self.bot.get_guild(Config.HUB_GUILD_ID)
        if self.guild:
            self.commands = self.guild.get_channel(Config.HUB_COMMANDS_ID)
            self.stdout = self.guild.get_channel(Config.HUB_STDOUT_ID)
            if self.stdout:
                await self.stdout.send(f"Modmail v{modmail.__version__} is online!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if self.bot.user in message.mentions or "all" in message.content:
            if message.channel == self.commands:
                if message.content.lower().startswith("shutdown"):
                    await self.bot.close()


def setup(bot: modmail.bot.Bot) -> None:
    bot.add_cog(Hub(bot))
