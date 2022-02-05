import discord


check = '\U00002705'


class WordleClient(discord.Client):

    def __init__(self, watch_channel, message_manager, command_handler):
        discord.Client.__init__(self)
        self._watch_channel = watch_channel
        self._message_manager = message_manager
        self._command_handler = command_handler

    async def on_ready(self):
        print(f'{self.user} has connected to discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.name != self._watch_channel:
            return

        response_type, response = await self._command_handler.handle_command(message.guild, message)
        if response_type == self._command_handler.Response.NONE:
            ok = self._message_manager.handle(message.guild.id, message.author.id, message.content, message.created_at)
            if ok:
                await message.add_reaction(check)
        elif response_type == self._command_handler.Response.SCRAPE:
            await self.scrape(message.channel)
        elif response_type == self._command_handler.Response.MSG_CHANNEL:
            await message.channel.send(response)
        elif response_type == self._command_handler.Response.MSG_PRIVATE:
            await message.author.send(response)

    async def scrape(self, channel):
        async for message in channel.history(limit=500):
            if check not in [str(r) for r in message.reactions]:
                ok = self._message_manager.handle(message.guild.id, message.author.id, message.content,
                                                  message.created_at)
                if ok:
                    await message.add_reaction(check)
