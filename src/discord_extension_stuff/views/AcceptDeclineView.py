from typing import Optional

import discord


class AcceptDeclineView(discord.ui.View):
    message: Optional[discord.Message]
    decision: Optional[bool]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decision = None
        self.message = None

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        await self.disable_all_items()

    @discord.ui.button(label="Accept",
                       style=discord.ButtonStyle.green,
                       custom_id="accept")
    async def on_accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.decision = True
        await self.disable_all_items()
        self.stop()

    @discord.ui.button(label="Decline",
                       style=discord.ButtonStyle.red,
                       custom_id="decline")
    async def on_decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.decision = False
        await self.disable_all_items()
        self.stop()
