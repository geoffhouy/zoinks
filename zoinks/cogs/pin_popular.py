import config

import discord

import logging


logger = logging.getLogger(__name__)


class PinPopular:

    def __init__(self, bot):
        self.bot = bot
        self.pin_threshold = 10
        self.disabled_channels = (462996078430781441, 462996375794221066, 462996408216059914, 462996435839877130)
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_raw_reaction_add(self, payload):
        if payload.guild_id == config.COOLSVILLE_GUILD_ID:
            if payload.channel_id not in self.disabled_channels:
                channel = self.bot.get_channel(payload.channel_id)
                if len(await channel.pins()) < 50:
                    message = await channel.get_message(payload.message_id)
                    if not message.pinned:
                        reaction = next((reaction for reaction in message.reactions
                                         if reaction.count >= self.pin_threshold), None)
                        if reaction is not None:
                            await message.pin()
                            await _send_pin_message(channel, message, reaction)
                            logger.info(f'Message by {message.author} pinned')


def setup(bot):
    bot.add_cog(PinPopular(bot))


async def _send_pin_message(channel, message, reaction):
    embed = discord.Embed(description=message.content, color=0x4D9C5F, timestamp=message.created_at)
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    embed.set_footer(text=f'Auto-pinned with {reaction.count} {reaction.emoji}')
    if message.embeds:
        embed.set_image(url=message.embeds[0].url)
    await channel.send(embed=embed)
