from discord.ext import commands


class MyHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    def get_command_signature(self, command):
        aliases = '|'.join(command.aliases)
        params = " ".join(f"<{param.name}>" for param in command.clean_params.values())
        signature = f'{self.context.clean_prefix}{command.name}'
        if aliases:
            signature = f'{signature} ({aliases})'
        if params:
            signature = f'{signature} {params}'
        return signature

    async def send_bot_help(self, mapping):
        bot = self.context.bot
        ctx = self.context

        for cog, cog_commands in mapping.items():
            if cog:
                if len(cog_commands) == 0:
                    continue

                self.paginator.add_line('')
                self.paginator.add_line(f'{cog.qualified_name}:')

            for command in cog_commands:
                self.paginator.add_line('')  # Extra line
                self.paginator.add_line(self.get_command_signature(command))
                if command.help:
                    docstring_lines = command.help.split('\n')
                    self.paginator.add_line(docstring_lines[0])  # Display the first line of the docstring
                else:
                    self.paginator.add_line("No description available")

        self.paginator.add_line('')
        self.paginator.add_line(f"Type `{ctx.prefix}help command` for more info on a command.")

        await self.send_pages()
