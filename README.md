# StupidAlentoBot
A Discord bot that's stupid and made by me, Alento. It contains a modular framework relying on PyYAML and Discord.py, with 
multiple helpers for bot developers, and multiple modules for bot users.

## Requirements
* Python 3.8+
* discord.py
* pyyaml

As of writing this, several discord.py dependencies do not have 3.9 wheels built for Windows. You are better off 
specifically installing Python 3.8.x in that case

## Tested Environment
* Ubuntu 20.04 with Python 3.8.6
* Ubuntu 20.10 with Python 3.8.6
* Mint 19.3 with Python 3.8.6

# Setup and Running
This section contains instructions on how to get the bot up and running.
## Installation
1) Clone or download this repository and put it on disk. Unzip if needed and open a terminal/command prompt in the 
repository folder.
2) (Optional) Create a virtual environment inside the cloned/unzipped repo (`python3 -m venv venv`) and activate it. 
(`source venv/bin/activate`)
    1) Ubuntu (Linux) - `python3 -m venv venv` to create and `source venv/bin/activate` to activate.
    2) Windows - `py -m venv venv` to create and `venv/Scripts/activate.bat` to activate.
3) Install the dependencies. 
    1) Ubuntu (Linux) - `pip3 install -r requirements.txt`
    2) Windows - `py -m pip install -r requirements.txt`
    
## First Run
If installed correctly, running `start.py` (Windows, `py start.py` - Ubuntu, `python3 start.py`) should yield logger 
messages and exit immediately.

One of the logger messages should mention putting your discord token in `config.yaml`, which should be done at this 
step. [You can get your token from the bot portion of your application.](https://discord.com/developers/applications) 
You need to have both PRESENCE INTENT and SERVER MEMBERS INTENT enabled for your bot.

Inside `config.yaml` you can change the bot prefix, where data is stored, and the invite link for the `invite` command.

## Continued Setup and Running.
1) If you want to use existing modules, uncomment the ones you wish to use in `start.py`
2) Run `start.py`
    1) Ubuntu (Linux) - `python3 start.py`
    2) Windows - `py start.py`

# Development
This section contains instructions on how to use the various helpers that the bot gives you to aid in Discord bot development.
## Order of Startup
1) Alento Bot begins Initialization.
    1) Storage begins Initialization.
        1) Config is loaded.
        2) Data directories are created. (if needed)
        3) Cache, guild, and user storage are initialized.
    2) Logging is configured.
    3) Legacy Module is initialized and added to Alento Bot.
2) Modules are added to Alento Bot.
3) Modules added are initialized. Note, modules may not be initialized in the order they are added.
    1) Caches are likely added and loaded here.
    2) Guild and User data are likely added here.
4) Cogs are initialized.
    1) Autosave loop is started but does not save on the first run.
    2) Timer loop is started.
5) Load method for all modules is called.
6) Bot does final setup.
    1) Checks for Discord token. If not found, aborts running the bot.
    2) Changes prefix if changed in config.
7) Begins the Discord.py bot loop.
## Modules
This allows for easy adding and removing specific sections of the bot, but still allows for the flexibility of having a 
class controlling the cogs.

Example code for a module with a single cog:
```python
from alento_bot import BaseModule
from discord.ext import commands

class ExampleModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.add_cog(ExampleCog())


class ExampleCog(commands.Cog, name="Example Cog"):
    @commands.command(name="example")
    async def example_command(self, context: commands.Context):
        await context.send("Hello there!")
```
Base module bits:
* `BaseModule.add_cog()`: Used to add cogs to the module.
* `BaseModule.load()`: Overwide with no arguments (other than self) to have code execute on bot startup.
* `BaseModule.save()`: Override with no arguments (other than self) to have code execute on bot shutdown.
* `BaseModule.bot`: Gives access to the `discord.ext.commands.Bot` object.
* `BaseModule.storage`: Gives access to the `StorageManager` object.
* `BaseModule.timer`: Gives access to the upcoming Timer object.


## Storage Manager
This makes it trivial to store variables on your disk as a central cache, per-guild data, or per-user data, all with autoloading
and saving.

Cache is aimed to be a single, cross-server/user storage class. Guilds is meant to be per-guild (AKA server), user is 
per user.

Example code for all three types of storage:
```python
from alento_bot import StorageManager, BaseModule, user_data_transformer, guild_data_transformer, cache_transformer
from discord.ext import commands


@cache_transformer(name="example_cache_data")
class ExampleCacheData:
    def __init__(self):
        self.global_uses = 0


@user_data_transformer(name="example_user_data")
class ExampleUserData:
    def __init__(self):
        self.guild_uses = 0

@guild_data_transformer(name="example_guild_data")
class ExampleGuildData:
    def __init__(self):
        self.user_uses = 0

class ExampleModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.cache = self.storage.caches.register_cache("example_cache_data", self.cache)
        self.storage.guilds.register_data_name("example_guid_data", ExampleGuildData)
        self.storage.users.register_data_name("example_user_data", ExampleUserData)
        
        self.add_cog(ExampleCog(self.storage, self.cache))

class ExampleCog(commands.Cog, name="Example"):
    def __init__(self, storage: StorageManager, cache: ExampleCacheData):
        self.storage = storage
        self.cache = cache
    
    @commands.guild_only()
    @commands.command(name="example", description="Example description text.", brief="Example brief text.")
    async def example_command(self, context: commands.Context, *args):
        guild_data = self.storage.guilds.get(context.guild.id, "example_guild_data")
        user_data = self.storage.users.get(context.author.id, "example_user_data")
        self.cache.global_uses += 1
        guild_data.guild_uses += 1
        user_data.user_uses += 1
        await context.send(f"Example: Global uses `{self.cache.global_uses}`, Server uses {guild_data.guild_uses}, "
                           f"User uses: {user_data.user_uses}")
```
## Timers
This is used to easily add not-very-accurate timed events to the bot. Roughly once a minute, the bot will loop through all the given timer events and check if they should be executed, so expect up to 1 minute of inaccuracy. No timer data is saved to disk.

To make a timer, you must provide a unique identifier string (could be your module name + datetime the timer goes off), the datetime the coroutine should be run at, and a coroutine to execute.

Example timer:

```py
from datetime import datetime, timedelta


class TimerTestCog(commands.Cog):
    def __init__(self, timer: TimerManager):
        self.timer = timer

    @commands.command(name="fivemintimer")
    async def fivemintimer(self, context):
        time_now = datetime.utcnow()
        self.timer.add_timer(f"fivemintimer_{time_now}", time_now + timedelta(minutes=5),
                             self.on_five_minute_timer(context))

    async def on_five_minute_timer(self, context):
        await context.send("It's been roughly 5 minutes!")
```
