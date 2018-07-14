import logging


logger = logging.getLogger(__name__)


async def in_rules_channel(ctx):
    return ctx.guild is not None and ctx.message.channel.name == 'rules'
