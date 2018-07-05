import discord

import logging


logger = logging.getLogger(__name__)


class PinPopular:
    """Represents a cog for a Discord bot.

    This cog extends the default on_raw_reaction_add event function. Note: on_raw_reaction_add does not
    use the bot's message cache which means old messages can be pinned.
    It uses Discord's built-in reactions to pin the 'popular' message in its channel
    on the specified guild.

    *The guild is specified at the time of creation of the bot. See its config attribute.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot.
    pin_threshold: int
        The number of same-emoji reactions required for a message to become 'popular'/pinned.
    """
    def __init__(self, bot):
        self.bot = bot
        self.pin_threshold = 10
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_raw_reaction_add(self, payload):
        if payload.guild_id == self.bot.config.guild.id:
            if payload.channel_id not in self.bot.config.pin_disabled_channels:
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
