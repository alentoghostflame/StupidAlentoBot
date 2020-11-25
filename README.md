# StupidAlentoBot
Discord bot that's stupid and made by me, Alento. Contains a modular framework relying on PyYAML and Discord.py, with multiple helpers for bot developers, and multiple modules for bot users.

## Requirements
* Python 3.8+
* discord.py
* pyyaml

As of this writing, several discord.py dependencies do not have 3.9 wheels built for Windows. You are better off specifically installing Python 3.8.x in that case

## Tested Environment
* Ubuntu 20.04 with Python 3.8.6
* Ubuntu 20.10 with Python 3.8.6

# Setup and Running
This section contains instructions on how to get the bot up and running.
## Installation
1) Clone or download this repository and put it on disk. Unzip if needed and open a terminal/command prompt in the repository folder.
2) (Optional) Create a virtual environment inside the cloned/unzipped repo (`python3 -m venv venv`) and activate it. 
(`source venv/bin/activate`)
    1) Ubuntu (Linux) - `python3 -m venv venv` to create and `source venv/bin/activate` to activate.
    2) Windows - `py -m venv venv` to create and `venv/Scripts/activate.bat` to activate.
3) Install the dependencies. 
    1) Ubuntu (Linux) - `pip3 install -r requirements.txt`
    2) Windows - `py -m pip install -r requirements.txt`
    
## First Run
If installed correctly, running `start.py` (Windows, `py start.py` - Ubuntu, `python3 start.py`) should yield logger messages and exit immediately.

One of the logger messages should mention putting your discord token in `config.yaml`, which should be done at this step. [You can get your token from the bot portion of your application.](https://discord.com/developers/applications) You need to have both PRESENCE INTENT and SERVER MEMBERS INTENT enabled for your bot.

Inside `config.yaml` you can change the bot prefix, where data is stored, and the invite link for the `invite` command.

## Continued Setup and Running.
1) If using existing modules, uncomment the ones you wish to use in `start.py`
2) Run `start.py`
    1) Ubuntu (Linux) - `python3 start.py`
    2) Windows - `py start.py`

# Development
This section contains instructions on how to use the various helpers the bot gives you to aid in Discord bot development.
## Modules
Allows for easily adding and removing specific sections of a bot, but still allows for the flexibility of having a class controlling the cogs.

Example code for a module with a single cog:
```
from alento_bot import BaseModule
from discord.ext import commands

class ExampleModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.add_cog(ExampleCog())


class ExampleCog(commands.Cog, name="Example"):
    @commands.command(name="example")
    async def example_command(self, context: commands.Context, *args):
        await context.send("Hello there!")
```
