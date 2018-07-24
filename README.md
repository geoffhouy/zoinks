# ZOINKS

ZOINKS is a Discord bot that automates boring stuff, provides interactive games, and records simple statistics for my personal Discord server. At the moment, ZOINKS has no database integration.

### Features
- Built-in Asynchronous Web Scraping - Fetches data from websites, formats and posts data to Discord when new data is retrieved.
  - Currently provides patch notes for [League of Legends](https://i.imgur.com/Nsx2Mpc.png), [Dota 2](https://i.imgur.com/DXTNMZx.png), [Overwatch](https://i.imgur.com/KT5aGzc.png), [Fortnite](https://i.imgur.com/W8YztK0.png), [Realm Royale](https://i.imgur.com/uJ82M1z.png), [RuneScape](https://i.imgur.com/9Z97C9O.png), [Minecraft](https://i.imgur.com/fEp0pFD.png), and [Darkest Dungeon](https://i.imgur.com/Qt9mjzh.png).
- Message-based, Interactive Games - Provides a plug-and-playable Mad Libs and a scrambled word puzzle game.
- New Member Handling - Assigns all new members the `Guest` role and sends them a welcome message with a link to the `#rules` channel.
- Content Creator Notifications - Uses built-in Discord features to notify the specified server of `Content Creator` activity.
- Popular Message Pinning - Pins a message once it receives a certain number of reactions.
- League of Legends Commands - Uses data directly from Riot Games' API.
  - Currently provides the [`profile [region] [summoner name]`](https://i.imgur.com/7EgwC2k.png) command

### Plans
- Add League of Legends (in progress) and Fortnite profile commands
- Add music player
- Add database integration

### How To Use
At this time, I'm unable to run the bot 24/7, so feel free to run an instance of this bot yourself. To do so, be sure to perform the following steps:
1. Install Python 3.6 or higher.
2. Download this project.
3. Install external libraries by entering `python3.6 -m pip install -U -r requirements.txt` into a terminal.
4. Edit the existing `config.py` constants with your bot's details and Riot Games API key.
5. Edit the existing `zoinks/cogs/coolsville.py` constants with your server's details.
6. Edit the existing `zoinks/cogs/web_scrapers.py` constants with your preferred output channels.
7. Run `launcher.py` by entering `python3.6 launcher.py` into a terminal.

Note: Some Python knowledge is required to further personalize the bot.

### Requirements
See [requirements.txt](https://github.com/geoffhouy/zoinks/blob/master/requirements.txt).

### Credits
[Discord](https://discordapp.com/)  
[@Rapptz](https://github.com/Rapptz) for [discord.py (rewrite)](https://github.com/Rapptz/discord.py/tree/rewrite)

### License
See [LICENSE](https://github.com/geoffhouy/vexillarius/blob/master/LICENSE).
