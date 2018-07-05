
DISCORD_CLIENT_ID = ''
DISCORD_TOKEN = ''
DISCORD_WEBHOOK_URL = ''


class Coolsville:

    GUILD_ID = 0
    RULES_CHANNEL_ID = 0
    NOTIFICATIONS_CHANNEL_ID = 0
    PIN_DISABLED_CHANNELS = (0, 1, 2, 3)

    def __init__(self):
        self.guild = None
        self.rules_channel = None
        self.notifications_channel = None
        self.pin_disabled_channels = ()

    def configure(self, guild, rules_channel, notification_channel):
        self.guild = guild
        self.rules_channel = rules_channel
        self.notifications_channel = notification_channel
        self.pin_disabled_channels = self.__class__.PIN_DISABLED_CHANNELS
