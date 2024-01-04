from discord.ext import commands


class MyHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    def get_command_signature(self, command) -> str:
        aliases = '|'.join(command.aliases)
        signature = f'{self.context.clean_prefix}{command.name}'
        if aliases:
            signature = f'{signature} ({aliases})'

        for param in command.clean_params.values():
            signature += f'\n<{param.name}>'
            if param.default is not param.empty:
                signature += f" (default: {param.default})"
            else:
                signature += " (no default)"
            if param.description:
                signature += f": {param.description}"

        return signature

    async def send_bot_help(self, mapping):
        cogs_with_commands = sorted((cog for cog in mapping.keys() if cog), key=lambda cog_: cog_.qualified_name)
        for cog in cogs_with_commands:
            commands_in_cog = sorted(cog.get_commands(), key=lambda cmd_: cmd_.name)
            self.paginator.add_line(f'{cog.qualified_name}:')
            for command in commands_in_cog:
                self.paginator.add_line(self.get_command_signature(command))
            self.paginator.add_line('')

        self.paginator.add_line(self.get_ending_note())
        await self.send_pages()

    async def send_command_help(self, command):
        self.paginator.add_line(self.get_command_signature(command))
        if command.help:
            docstring_lines = command.help.split('\n')
            for line in docstring_lines:
                self.paginator.add_line(line)
        else:
            self.paginator.add_line("No description available")
        await self.send_pages()

    async def send_cog_help(self, cog):
        self.paginator.add_line(f'`{cog.qualified_name}` Commands:')
        for command in cog.get_commands():
            self.paginator.add_line(self.get_command_signature(command))
        await self.send_pages()

    def get_ending_note(self):
        return ("Type `{0}help command` for more info on a command.\n"
                "You can also type `{0}help category` for more info on a category.").format(self.context.clean_prefix)
