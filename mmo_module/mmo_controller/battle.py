from mmo_module.mmo_controller.mmo_server import MMOServer
from mmo_module.mmo_data import BaseCharacter
from discord.ext import commands, tasks
from asyncio import sleep
from typing import Dict
import discord


BASIC_ATTACK = "Basic Attack"
ENEMY_ATTACK_WAIT = 12
PLAYER_ATTACK_WAIT = 8


class MMOBattleManager:
    def __init__(self, mmo_server: MMOServer):
        self._mmo_server: MMOServer = mmo_server
        self._battle_instances: Dict[int, MMOBattleInstance] = dict()

    async def create_battle(self, context: commands.Context):
        battle_instance = MMOBattleInstance(self._mmo_server, context, self.cleanup_battle)
        self._battle_instances[context.author.id] = battle_instance

        await battle_instance.start_battle()

    async def attack(self, context: commands.Context, attack_name: str):
        if context.author.id in self._battle_instances:
            battle_instance = self._battle_instances[context.author.id]
            await battle_instance.change_attack(context, attack_name)
        else:
            await context.send("NO BATTLES.")

    def cleanup_battle(self, user_id: int):
        if user_id in self._battle_instances:
            self._battle_instances.pop(user_id)


class MMOBattleInstance:
    def __init__(self, mmo_server: MMOServer, context: commands.Context, cleanup_func):
        # self._bot: commands.Bot = bot
        self._mmo_server: MMOServer = mmo_server
        self._original_context: commands.Context = context
        self._original_message: discord.Message = context.message
        self._player: BaseCharacter = self._mmo_server.user.get(context.author.id)
        self._enemy: BaseCharacter = BaseCharacter()
        self._enemy_dead: bool = False
        self._player_dead: bool = False
        self._cleanup = cleanup_func
        self._player_task = None
        self._enemy_task = None
        self.player_attack = "Default Attack"

    async def display_hp(self):
        embed = discord.Embed(title="Battle", color=0xc63a43)
        embed.add_field(name="Player", value=f"{self._player.get_health()}/{self._player.max_health}", inline=True)
        embed.add_field(name="Enemy", value=f"{self._enemy.get_health()}/{self._enemy.max_health}", inline=True)
        if self._original_message.content:
            await self._original_message.edit(content=None, embed=embed)
        else:
            await self._original_message.edit(embed=embed)

    async def start_battle(self):
        self._original_message = await self._original_context.send("Starting battle in 3")
        await sleep(1)
        # await self._original_context.send("2.")
        await self._original_message.edit(content="2.")
        await sleep(1)
        await self._original_message.edit(content="1!")
        await sleep(1)
        await self._original_message.edit(content="GO.")
        await sleep(1)
        self._player_task = self.player_tick.start(self._original_context)
        self._enemy_task = self.enemy_tick.start(self._original_context)
        await self.display_hp()

    async def end_battle(self):
        self._player_task.cancel()
        self._enemy_task.cancel()

        if self._enemy_dead:
            await self._original_context.send("Player won the battle!")
        elif self._player_dead:
            await self._original_context.send("Enemy won the battle!")
        else:
            await self._original_context.send("The battle was canceled, tie!")
        self._cleanup(self._original_context.author.id)

    async def change_attack(self, context: commands.Context, attack_name: str):
        self.player_attack = attack_name
        await context.send(f"Changed attack to {self.player_attack}.")

    @tasks.loop(seconds=PLAYER_ATTACK_WAIT)
    async def player_tick(self, context: commands.Context):
        self._enemy.modify_health(-20)
        await context.send(f"Player used {self.player_attack}, dealing 20 damage!")
        await self.display_hp()

        if self._enemy.get_health() <= 0:
            self._enemy_dead = True
            await self.end_battle()

    @tasks.loop(seconds=ENEMY_ATTACK_WAIT)
    async def enemy_tick(self, context: commands.Context):
        self._player.modify_health(-10)
        await context.send("Enemy attacked, dealing 10 damage!")
        await self.display_hp()

        if self._player.get_health() <= 0:
            self._player_dead = True
            await self.end_battle()
