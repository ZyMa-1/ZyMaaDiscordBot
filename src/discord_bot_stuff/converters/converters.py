from discord.ext import commands
from ossapi import GameMode, Mod

from factories import UtilsFactory


class GameModeConverter(commands.Converter):
    async def convert(self, ctx, argument) -> GameMode:
        try:
            return GameMode(argument)
        except ValueError:
            raise commands.BadArgument(f"{argument} is not a valid value for 'GameMode' argument")


class ModsConverter(commands.Converter):
    async def convert(self, ctx, argument) -> Mod:
        try:
            return Mod(argument)
        except ValueError:
            raise commands.BadArgument(f"{argument} is not a valid value for 'Mod' argument")


class OsuUserIdConverter(commands.Converter):
    async def convert(self, ctx, argument) -> int:
        osu_api_utils = UtilsFactory.get_osu_api_utils()
        if not argument.isnumeric():
            raise commands.BadArgument("Sorry, but osu user id must be numeric")

        if not await osu_api_utils.check_if_user_exists(int(argument)):
            raise commands.BadArgument("Sorry, but osu user with specified id does not exist")

        return int(argument)
