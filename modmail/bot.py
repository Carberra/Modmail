# Copyright (c) 2021, Carberra Tutorials
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import os

import hikari
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lightbulb import errors, events
from lightbulb.app import BotApp
from pytz import utc

import modmail
from modmail import Config

log = logging.getLogger(__name__)

bot = BotApp(
    Config.TOKEN,
    default_enabled_guilds=Config.GUILD_ID,
    case_insensitive_prefix_commands=True,
    intents=hikari.Intents.ALL,
    cache_settings=hikari.CacheSettings(
        components=hikari.CacheComponents.GUILDS | hikari.CacheComponents.MEMBERS
    ),
)

bot.d.scheduler = AsyncIOScheduler()
bot.d.scheduler.configure(timezone=utc)

bot.load_extensions_from("./modmail/extensions")


@bot.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.scheduler.start()


@bot.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    await bot.rest.create_message(
        Config.STDOUT_CHANNEL_ID,
        f"Modmail is now online! (Version {modmail.__version__})",
    )


@bot.listen(hikari.StoppingEvent)
async def on_stopping(event: hikari.StoppingEvent) -> None:
    bot.d.scheduler.shutdown()

    await bot.rest.create_message(
        Config.STDOUT_CHANNEL_ID,
        f"Modmail is shutting down. (Version {modmail.__version__})",
    )


@bot.listen(events.CommandErrorEvent)
async def on_command_error(event: events.CommandErrorEvent) -> None:
    exc = getattr(event.exception, "__cause__", event.exception)

    if isinstance(exc, errors.NotOwner):
        await event.context.respond("You need to be an owner to do that.")
        return

    await event.context.respond(
        "Something went wrong. Open an issue on the GitHub repository."
    )
    raise event.exception


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot.run(
        activity=hikari.Activity(
            name=f"DM reports • Version {modmail.__version__}",
            type=hikari.ActivityType.LISTENING,
        )
    )
