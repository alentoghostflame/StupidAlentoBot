from alento_bot import StorageManager, BaseModule, user_data_transformer, error_handler, universal_text, \
    guild_data_transformer, TimerManager
from datetime import datetime, timedelta
from typing import Dict, Optional
from discord.ext import commands, tasks
from asyncio import sleep
import discord
import random


PILLOW_PHASE_INIT = "init"
PILLOW_PHASE_PRESTART = "prestart"
PILLOW_PHASE_POSTSTART = "poststart"
PILLOW_PHASE_DONE = "done"


PILLOW_PRESTART_MSGS = ["{} grabs a pillow!", "{} equips a pillow!"]
PILLOW_POSTSTART_MSGS = ["{} launches in mid-fight!", "{} pops in from the sidelines!"]


class PillowFightPlayerData:
    def __init__(self, member: discord.Member):
        self.member = member
        self.health = 100
        self.damage_low = 0
        self.damage_high = 20
        self.damage_crit = 30
        self.chance_miss = 0.2
        self.chance_crit = 0.05
        self.napping = False
        self.cooldown: timedelta = timedelta(seconds=3)
        self.last_attack: Optional[datetime] = None

    def deal_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.napping = True


class PillowFightInstance:
    def __init__(self, timer: TimerManager, channel: discord.TextChannel):
        self.timer: TimerManager = timer
        self.players: Dict[int, PillowFightPlayerData] = dict()
        self.channel = channel
        self.phase = PILLOW_PHASE_INIT
        # self.start_fight_loop = tasks.Loop(self._start, 30, 0, 0, 1, True, False)
        # self.post_fight_loop = tasks.Loop(self._post_pillow_fight, 30, 0, 0, 1, True, False)

    async def _start(self):
        await sleep(15)
        await self.channel.send("Pillow fight begins in 15 seconds!")
        await sleep(5)
        await self.channel.send("Pillow throwdown in 10!")
        await sleep(5)
        for i in range(5):
            await self.channel.send(f"{5 - i}!")
            await sleep(1)
        self.phase = PILLOW_PHASE_POSTSTART
        await self.channel.send("WALLOP!")
        self._post_pillow_fight.start()

    async def join(self, member: discord.Member):
        if member.id in self.players:
            await self.channel.send("You're already in the pillow fight!")
        else:
            self.players[member.id] = PillowFightPlayerData(member)
            if self.phase == PILLOW_PHASE_INIT:
                await self.channel.send(f"{member.mention} challenges everyone to a pillow fight!")
                self.phase = PILLOW_PHASE_PRESTART
                await self._start()
            elif self.phase == PILLOW_PHASE_PRESTART:
                await self.channel.send(random.choice(PILLOW_PRESTART_MSGS).format(member.mention))
            elif self.phase == PILLOW_PHASE_POSTSTART:
                await self.channel.send(random.choice(PILLOW_POSTSTART_MSGS).format(member.mention))
            else:
                await self.channel.send(f"Uh, you're not supposed to see this. Phase=`{self.phase}` Give that to "
                                        f"Alento, but uh, going to pretend this is post-start.")
                await self.channel.send(random.choice(PILLOW_POSTSTART_MSGS).format(member.mention))

    async def attack(self, attacker: discord.Member, victim: discord.Member, attack_term: str):
        time_now = datetime.utcnow()
        if attacker.id not in self.players:
            await self.join(attacker)
        att_data = self.players[attacker.id]
        if self.phase != PILLOW_PHASE_POSTSTART:
            await self.channel.send("You can't hit people yet, the pillow fight hasn't begun!")
        elif att_data.napping:
            await self.channel.send("You can't hit people, you're taking a nap!")
        elif att_data.last_attack and time_now < att_data.last_attack + att_data.cooldown:
            await self.channel.send("You're trying to swing too fast, wait a little bit!")
        else:
            if victim.id in self.players:
                vic_data = self.players[victim.id]
                if vic_data.napping:
                    await self.channel.send("You can't hit them, they're already taking a nap!")
                else:
                    self._post_pillow_fight.restart()
                    random_num = random.random()
                    if random_num < att_data.chance_miss:
                        await self.channel.send(f"{attacker.display_name} missed {victim.display_name}!")
                    elif (1 - att_data.chance_crit) < random_num:
                        vic_data.deal_damage(att_data.damage_crit)
                        await self.channel.send(f"WHAAAAAAAM! {attacker.mention} critted {victim.mention} for "
                                                f"{att_data.damage_crit} damage!")
                    else:
                        damage = random.randint(att_data.damage_low, att_data.damage_high + 1)
                        vic_data.deal_damage(damage)
                        # await self.channel.send(f"{attacker.mention} did {damage} damage to {victim.mention}!")
                        await self.channel.send(f"{attacker.display_name} {attack_term} {victim.display_name} for "
                                                f"{damage} damage!")
                    att_data.last_attack = time_now
                    if vic_data.napping:
                        await self.channel.send(f"{attacker.mention} {attack_term} {victim.mention} into naptime!")

                    if winner := self.check_for_win():
                        await self.handle_win(winner)

            else:
                await self.channel.send(f"{attacker.mention}, that person isn't in this fight (yet)!")

    @tasks.loop(seconds=30, count=1)
    async def _post_pillow_fight(self):
        await sleep(30)
        self.phase = PILLOW_PHASE_DONE
        await self.channel.send("Oof, looks like everyone's all pooped out! Pillow fight over!")

    def check_for_win(self) -> Optional[discord.Member]:
        winner = None
        for member_id in self.players:
            if not self.players[member_id].napping:
                if not winner:
                    winner = self.players[member_id].member
                else:
                    return None
        if winner is None:
            raise ValueError("Winner is none, nobody won? What is going on?")
        else:
            return winner

    async def handle_win(self, member: discord.Member):
        self.phase = PILLOW_PHASE_DONE
        self._post_pillow_fight.cancel()
        await self.channel.send(f"In the end, {member.mention} was the one that came out victorious! Good pillow "
                                f"fight!")


@user_data_transformer(name="example_user_data")
class ExampleUserData:
    def __init__(self):
        self.example_count = 0


@guild_data_transformer(name="battle_config")
class GuildBattleConfig:
    def __init__(self):
        self.pillow_fight_enabled: bool = True


class BattleModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.storage.guilds.register_data_name("battle_config", GuildBattleConfig)
        self.add_cog(BattleCog(self.storage, self.timer))


class BattleCog(commands.Cog, name="Battles"):
    def __init__(self, storage: StorageManager, timer: TimerManager):
        self.storage = storage
        self.timer = timer
        self.active_pillow_fights: Dict[int, PillowFightInstance] = dict()

    def clean_pillow_fight(self, guild_id: int):
        if (pillow_instance := self.active_pillow_fights.get(guild_id, None)) and \
                pillow_instance.phase == PILLOW_PHASE_DONE:
            self.active_pillow_fights.pop(guild_id)

    @commands.group(name="pf", brief="Pillow fight commands.", invoke_without_command=True)
    async def pf(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @pf.command(name="info", brief="Shows pillow fight server info")
    async def pf_info(self, context: commands.Context):
        config: GuildBattleConfig = self.storage.guilds.get(context.guild.id, "battle_config")
        embed = discord.Embed(title="Pillow Fight", color=0xffffff)
        embed.add_field(name="Enabled", value=f"{config.pillow_fight_enabled}")
        await context.send(embed=embed)

    @pf.command(name="start", brief="Declares a pillow fight on the server that ANYONE can join!")
    async def pf_start(self, context: commands.Context):
        self.clean_pillow_fight(context.guild.id)
        if context.guild.id in self.active_pillow_fights:
            await context.send("A pillow fight is already going on!")
        else:
            self.active_pillow_fights[context.guild.id] = PillowFightInstance(self.timer, context.channel)
            await self.active_pillow_fights[context.guild.id].join(context.author)

    @pf.command(name="join", brief="Joins a pillow fight!")
    async def pf_join(self, context: commands.Context):
        self.clean_pillow_fight(context.guild.id)
        if pillow_instance := self.active_pillow_fights.get(context.guild.id, None):
            if pillow_instance.phase == PILLOW_PHASE_DONE:
                await context.send("The pillow fight is done, but still in the dictionary? You shouldn't see this!")
            elif context.channel.id != pillow_instance.channel.id:
                await context.send(f"You have to be in the channel the fight is going in: "
                                   f"{pillow_instance.channel.mention}")
            else:
                await pillow_instance.join(context.author)
        else:
            await context.send("There isn't an active pillow fight on this server.")

    @pf.command(name="wallop", brief="Wallop someone with a pillow!")
    async def pf_wallop(self, context: commands.Context, victim: discord.Member):
        await self.pillowfight_hit(context, victim, "wallop", "walloped")

    @pf.command(name="hit", brief="Hit someone with a pillow!")
    async def pf_hit(self, context: commands.Context, victim: discord.Member):
        await self.pillowfight_hit(context, victim, "hit", "hit")

    @pf.command(name="slam", brief="Slam someone with a pillow!")
    async def pf_slam(self, context: commands.Context, victim: discord.Member):
        await self.pillowfight_hit(context, victim, "slam", "slammed")

    async def pillowfight_hit(self, context: commands.Context, victim: discord.Member, present_tense: str,
                              past_tense: str):
        self.clean_pillow_fight(context.guild.id)
        if pillow_instance := self.active_pillow_fights.get(context.guild.id, None):
            if pillow_instance.phase == PILLOW_PHASE_POSTSTART:
                await pillow_instance.attack(context.author, victim, past_tense)
            else:
                await context.send(f"The pillow fight hasn't started, you can't {present_tense} anyone yet!")
        else:
            await context.send(f"You can't {present_tense} anyone, there isn't a pillow fight right now!")

    @commands.has_permissions(administrator=True)
    @pf.command(name="enable", brief="Enables pillow fights for this server.")
    async def pf_enable(self, context: commands.Context):
        config: GuildBattleConfig = self.storage.guilds.get(context.guild.id, "battle_config")
        if config.pillow_fight_enabled:
            await context.send(universal_text.FEATURE_ALREADY_ENABLED_FORMAT.format("Pillow Fight"))
        else:
            config.pillow_fight_enabled = True
            await context.send(universal_text.FEATURE_ENABLED_FORMAT.format("Pillow Fight"))

    @commands.has_permissions(administrator=True)
    @pf.command(name="disable", brief="Disables pillow fights for this server.")
    async def pf_disable(self, context: commands.Context):
        config: GuildBattleConfig = self.storage.guilds.get(context.guild.id, "battle_config")
        if config.pillow_fight_enabled:
            config.pillow_fight_enabled = False
            await context.send(universal_text.FEATURE_DISABLED_FORMAT.format("Pillow Fight"))
        else:
            await context.send(universal_text.FEATURE_ALREADY_DISABLED_FORMAT.format("Pillow Fight"))

    @pf.error
    @pf_enable.error
    @pf_disable.error
    @pf_join.error
    @pf_info.error
    @pf_wallop.error
    @pf_start.error
    async def cog_error_handler(self, context: commands.Context, exception: Exception):
        await error_handler(context, exception)
