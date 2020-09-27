from mmo_module.mmo_controller.mmo_server import MMOServer
from mmo_module.mmo_controller import text
from mmo_module.mmo_data import BaseCharacter, get_enemy
from discord.ext import commands, tasks
from asyncio import sleep
from typing import Dict, Set, List, Optional
import discord
import logging


logger = logging.getLogger("main_bot")


BASIC_ATTACK = "Basic Attack"
ENEMY_ATTACK_WAIT = 12
PLAYER_ATTACK_WAIT = 8


class MMOBattleManager:
    def __init__(self, mmo_server: MMOServer):
        self._mmo_server: MMOServer = mmo_server
        self._battle_instances: Dict[int, MMOBattleInstance] = dict()

    async def create_battle(self, context: commands.Context):
        self.cleanup_battle()
        if context.author.id in self._battle_instances.keys():
            await context.send(text.BATTLE_ALREAY_IN)
        else:
            player_character = self._mmo_server.user.get(context.author.id)
            enemy_character = get_enemy((max(0, player_character.xp.get_level() - 3),
                                         player_character.xp.get_level() + 1))
            battle_instance = MMOBattleInstance(self._mmo_server, context, [player_character], [enemy_character])
            self._battle_instances[context.author.id] = battle_instance
            await battle_instance.start()

    async def attack(self, context: commands.Context, attack_name: str):
        if context.author.id in self._battle_instances:
            battle_instance = self._battle_instances[context.author.id]
            await battle_instance.change_attack(context, attack_name)
        else:
            await context.send("NO BATTLES.")

    def cleanup_battle(self):
        for user_id in list(self._battle_instances.keys()):
            if self._battle_instances[user_id].done:
                self._battle_instances.pop(user_id)


# class MMOBattleInstance:
#     def __init__(self, mmo_server: MMOServer, context: commands.Context):
#         # self._bot: commands.Bot = bot
#         self._mmo_server: MMOServer = mmo_server
#         self._original_context: commands.Context = context
#         self._original_message: discord.Message = context.message
#         self._player: BaseCharacter = self._mmo_server.user.get(context.author.id)
#         self._enemy: BaseCharacter = BaseCharacter()
#         self._enemy_dead: bool = False
#         self._player_dead: bool = False
#         self._player_task = None
#         self._enemy_task = None
#         self.player_attack = "Default Attack"
#         self.done: bool = False
# class MMOBattleInstance:
#     def __init__(self, mmo_server: MMOServer, context: commands.Context, player1: BaseCharacter, player2: BaseCharacter):
#         self._mmo_server: MMOServer = mmo_server
#         self._original_context: commands.Context = context
#         self._first_message: discord.Message = context.message
#         self._player1: BaseCharacter = player1
#         self._player1_dead = False
#         self._player2: BaseCharacter = player2
#         self._player2_dead = False
#         self.player1_attack: str = "[PH]Tackle"
#         self.done: bool = False
#         self._task1 = tasks.Loop(self.player1_tick, 2 * self._player1.attack_speed, 0, 0, None, True, None)
#         self._task2 = tasks.Loop(self.player2_tick, 2 * self._player2.attack_speed, 0, 0, None, True, None)
#         self._task1.after_loop(self.end_battle)
#         # self._task2.after_loop(self.end_battle)


class MMOBattleInstance:
    def __init__(self, mmo_server: MMOServer, context: commands.Context, team1: List[BaseCharacter],
                 team2: List[BaseCharacter]):
        self._mmo_server: MMOServer = mmo_server
        self._original_context: commands.Context = context
        self._first_message: Optional[discord.Message] = None
        # self._players: List[BaseCharacter, ...] = list()
        self._team1: List[BaseCharacter] = team1
        self._team2: List[BaseCharacter] = team2
        self.done: bool = False
        # self._team1_index: Optional[int] = None
        # self._team2_index: Optional[int] = None

    def setup_teams(self):
        for char in self._team1:
            self.setup_char(char, True)
        for char in self._team2:
            self.setup_char(char, False)
        self._team1[0].combat.task.after_loop(self.battle_cleanup)

    def setup_char(self, char: BaseCharacter, on_team1: bool):
        if on_team1:
            char.combat.on_team1 = True
        char.combat.attack = "[PH]Tackle"
        char.combat.target = 0
        char.combat.alive = True
        char.combat.task = tasks.Loop(self.combat_tick, 2 * char.attack_speed, 0, 0, None, True, None)

    def cleanup_teams(self):
        for char in self._team1:
            self.cleanup_char(char)
        for char in self._team2:
            self.cleanup_char(char)

    # noinspection PyMethodMayBeStatic
    def cleanup_char(self, char: BaseCharacter):
        char.combat.on_team1 = None
        char.combat.attack = "[PH]Tackle"
        char.combat.target = None
        char.combat.alive = None
        char.combat.task = None

    async def start(self):
        self.setup_teams()
        self._first_message = await self._original_context.send("Starting battle in 3")
        await sleep(1)
        await self._first_message.edit(content="2.")
        await sleep(1)
        await self._first_message.edit(content="1!")
        await sleep(1)
        await self._first_message.edit(content="GO.")
        await sleep(1)
        self.start_tasks()
        await self.update_battle_board()

    def start_tasks(self):
        for char in self._team1:
            char.combat.task.start(char)
        for char in self._team2:
            char.combat.task.start(char)

    async def change_attack(self, context: commands.Context, attack_name: str):
        # self.player1_attack = attack_name
        # await context.send(text.PERSON_CHANGED_ATTACK.format(self.player1_attack))
        await context.send("PLACEHOLDER: Not currently implemented.")

#     async def player1_tick(self):
#         if not self._player1_dead:
#             await perform_combat_tick(self._original_context, self._player1, self._player2, self.player1_attack)
#             await self.display_hp()
#             if self._player2.health.get() <= 0:
#                 self._player2_dead = True
#                 self._task1.stop()
#         else:
#             self._task1.stop()

    async def combat_tick(self, char: BaseCharacter):
        if self.battle_finished():
            char.combat.task.stop()
        # elif char.health.get() <= 0:
        #     char.combat.alive = False
        #     await self._original_context.send(f"[PH]{char.get_name()} is down!")

        elif char.combat.alive:
            if char.health.get() > 0:
                char.tick()
                if char.combat.on_team1:
                    if not self._team2[char.combat.target].combat.alive:
                        char.combat.target = get_lowest_target(self._team2)
                    await perform_combat_tick(self._original_context, char, self._team2[char.combat.target])
                    await self.update_battle_board()
                else:
                    if not self._team1[char.combat.target].combat.alive:
                        char.combat.target = get_lowest_target(self._team1)
                    await perform_combat_tick(self._original_context, char, self._team1[char.combat.target])
                    await self.update_battle_board()
            else:
                char.combat.alive = False
            #     await self._original_context.send(f"[PH]{char.get_name()} is down!")

    def battle_finished(self) -> bool:
        if team_dead(self._team2) or team_dead(self._team1):
            return True
        else:
            return False

#     async def player2_tick(self):
#         if not self._player2_dead:
#             await perform_combat_tick(self._original_context, self._player2, self._player1, "[PH]Tackle")
#             await self.display_hp()
#             if self._player1.health.get() <= 0:
#                 self._player1_dead = True
#                 self._task2.stop()
#         else:
#             self._task2.stop()
#
#     async def display_hp(self):
#         embed = discord.Embed(title="Battle", color=0xc63a43)
#         embed.add_field(name="Player", value=get_battle_status_string(self._player1), inline=False)
#         embed.add_field(name="Enemy", value=get_battle_status_string(self._player2), inline=False)
#         if self._first_message.content:
#             await self._first_message.edit(content=None, embed=embed)
#         else:
#             await self._first_message.edit(embed=embed)

    async def update_battle_board(self):
        embed = discord.Embed(title="Battle", color=0xc63a43)
        # embed.add_field(name="Player", value=get_battle_status_string(self._player1), inline=False)
        embed.add_field(name="Attackers", value=get_team_status_string(self._team1), inline=False)
        # embed.add_field(name="Enemy", value=get_battle_status_string(self._player2), inline=False)
        embed.add_field(name="Defenders", value=get_team_status_string(self._team2), inline=False)
        if self._first_message.content:
            await self._first_message.edit(content=None, embed=embed)
        else:
            await self._first_message.edit(embed=embed)

#
#     async def end_battle(self):
#         logger.debug("End Battle Called.")
#         if not self.done:
#             logger.debug("Not Done, doing")
#             self.done = True
#             if self._player1_dead:
#                 self._player2.xp.adjust(self._player1.xp.get_worth())
#                 await self._original_context.send(text.BATTLE_PERSON_WON.format(self._player2.get_name(),
#                                                                                 self._player1.get_name(),
#                                                                                 self._player1.xp.get_worth()))
#             elif self._player2_dead:
#                 self._player1.xp.adjust(self._player2.xp.get_worth())
#                 await self._original_context.send(text.BATTLE_PERSON_WON.format(self._player1.get_name(),
#                                                                                 self._player2.get_name(),
#                                                                                 self._player2.xp.get_worth()))
#             else:
#                 await self._original_context.send("The battle was canceled, tie!")
#             if self._task1.is_running():
#                 self._task1.cancel()
#             if self._task2.is_running():
#                 self._task2.cancel()
#             await self._player1.context_tick(self._original_context)
#             self._player2.tick()
#             logger.debug("End Battle Ended.")
#         else:
#             logger.debug("Done, not doing.")

    async def perform_context_ticks(self):
        for char in self._team1:
            await char.context_tick(self._original_context)
        for char in self._team2:
            await char.context_tick(self._original_context)

    async def battle_cleanup(self):
        logger.debug("Battle cleanup called.")
        if team_dead(self._team2):
            xp_award = get_average_team_xp(self._team2)
            give_team_xp(self._team1, xp_award)
            await self._original_context.send(f"[PH]Attackers won, here's {xp_award} XP or something.")
        elif team_dead(self._team1):
            xp_award = get_average_team_xp(self._team1)
            give_team_xp(self._team2, xp_award)
            await self._original_context.send(f"[PH]Defenders won, here's {xp_award} XP or something.")
        else:
            await self._original_context.send("[PH]Something went wrong, neither team won? You aren't supposed to see "
                                              "this!")
        await self.perform_context_ticks()
        self.done = True


#
#     async def start_battle(self):
#         self._player.tick()
#         self._enemy.tick()
#         self._original_message = await self._original_context.send("Starting battle in 3")
#         await sleep(1)
#         # await self._original_context.send("2.")
#         await self._original_message.edit(content="2.")
#         await sleep(1)
#         await self._original_message.edit(content="1!")
#         await sleep(1)
#         await self._original_message.edit(content="GO.")
#         await sleep(1)
#         self._player_task = self.player_tick.start(self._original_context)
#         self._enemy_task = self.enemy_tick.start(self._original_context)
#         await self.display_hp()
#
#     async def end_battle(self):
#         if self._enemy_dead:
#             self._player.xp.adjust(50)
#             await self._original_context.send(text.BATTLE_PERSON_WON.format("Player", " and earned 50 XP"))
#         elif self._player_dead:
#             await self._original_context.send(text.BATTLE_PERSON_WON.format("Generic Enemy", ""))
#         else:
#             await self._original_context.send("The battle was canceled, tie!")
#         self._player.tick()
#         self.done = True
#
#     async def change_attack(self, context: commands.Context, attack_name: str):
#         self.player_attack = attack_name
#         await context.send(text.PERSON_CHANGED_ATTACK.format(self.player_attack))
#
#     @tasks.loop(seconds=PLAYER_ATTACK_WAIT)
#     async def player_tick(self, context: commands.Context):
#         self._player.tick()
#         self._enemy.health.adjust(-self._player.physical_damage)
#         await context.send(text.BATTLE_PERSON_DEALT_DAMAGE.format(context.author.name, self.player_attack, self._player.physical_damage))
#         await self.display_hp()
#
#         if self._enemy.health.get() <= 0:
#             self._enemy_dead = True
#             self._enemy_task.cancel()
#             await self.end_battle()


async def perform_combat_tick(context: commands.Context, player: BaseCharacter, target: BaseCharacter):
    player.tick()
    target.tick()
    target.health.adjust(-player.physical_damage)

    await context.send(text.BATTLE_DEALT_DAMAGE.format(player.get_name(), player.combat.attack, player.physical_damage,
                                                       target.get_name()))
    if target.health.get() <= 0:
        target.combat.alive = False
        await context.send(f"[PH]{target.get_name()} is down!")


def team_dead(team: List[BaseCharacter]) -> bool:
    all_dead = True
    for char in team:
        if char.combat.alive:
            all_dead = False
            break
    return all_dead


def get_lowest_target(team: List[BaseCharacter]) -> int:
    for i in range(len(team)):
        if team[i].combat.alive:
            return i
    return 0


#
#     @tasks.loop(seconds=ENEMY_ATTACK_WAIT)
#     async def enemy_tick(self, context: commands.Context):
#         self._enemy.tick()
#         self._player.health.adjust(-self._enemy.physical_damage)
#         await context.send(text.BATTLE_PERSON_DEALT_DAMAGE.format("Generic Enemy", "Basic Attack", self._enemy.physical_damage))
#         await self.display_hp()
#
#         if self._player.health.get() <= 0:
#             self._player_dead = True
#             self._player_task.cancel()
#             await self.end_battle()
#             self._enemy_task.cancel()


def get_average_team_xp(team: List[BaseCharacter]) -> int:
    xp_sum = 0
    for char in team:
        xp_sum += char.xp.get_worth()

    return xp_sum // len(team)


def give_team_xp(team: List[BaseCharacter], xp: int):
    for char in team:
        char.xp.adjust(xp)


def get_team_status_string(team: List[BaseCharacter]) -> str:
    output_str = ""

    for char in team:
        output_str += f"**{char.get_name()}**\n{get_battle_status_string(char)}\n"

    return output_str


def get_battle_status_string(player: BaseCharacter) -> str:
    return f"```{player.health.get_display()}\n{player.mana.get_display(2)}```"
