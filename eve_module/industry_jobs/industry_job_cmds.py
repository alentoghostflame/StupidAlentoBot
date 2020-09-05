from evelib import EVEManager, IndustryJob
from eve_module.storage import EVEUserAuthManager
from eve_module.industry_jobs import text
from discord.ext import commands
from datetime import datetime, timedelta
from typing import List
import logging
import discord


logger = logging.getLogger("main_bot")


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Industry Jobs", color=0x43464B)

    embed.add_field(name="Description", value=text.INDUSTRY_JOBS_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Permissions", value=text.INDUSTRY_JOBS_HELP_PERMISSIONS, inline=False)
    embed.add_field(name="Information", value=text.INDUSTRY_JOBS_HELP_INFORMATION, inline=False)

    await context.send(embed=embed)


async def enable_industry(user_auth: EVEUserAuthManager, context: commands.Context):
    if user_auth.set_selected_desired_scope(context.author.id, "esi-industry.read_character_jobs.v1", True):
        await context.send(text.INDUSTRY_JOBS_ENABLED)
    else:
        await context.send(text.INDUSTRY_JOBS_TOGGLE_FAIL)


async def disable_industry(user_auth: EVEUserAuthManager, context: commands.Context):
    if user_auth.set_selected_desired_scope(context.author.id, "esi-industry.read_character_jobs.v1", False):
        await context.send(text.INDUSTRY_JOBS_DISABLED)
    else:
        await context.send(text.INDUSTRY_JOBS_TOGGLE_FAIL)


async def send_industry_info(eve_manager: EVEManager, user_auth: EVEUserAuthManager, context: commands.Context):
    token = await user_auth.get_access_token(context.author.id, user_auth.get_selected(context.author.id))
    industry_jobs = await eve_manager.esi.industry.get_character_jobs(user_auth.get_selected(context.author.id), token)
    if industry_jobs:
        await send_industry_info_embed(industry_jobs, context)
    else:
        await context.send(text.INDUSTRY_JOBS_INFO_EMPTY)


async def send_industry_info_embed(industry_jobs: List[IndustryJob], context: commands.Context):
    embed = discord.Embed(title="Industry Info", color=0x43464B, timestamp=datetime.utcnow())

    manufacturing_string = ""
    rnd_time_eff_string = ""
    rnd_mat_eff_string = ""
    copying_string = ""
    reverse_eng_string = ""
    other_string = ""

    for job in industry_jobs:
        if job.activity_id == 1:
            manufacturing_string += get_industry_text(job)
        elif job.activity_id == 3:
            rnd_time_eff_string += get_industry_text(job)
        elif job.activity_id == 4:
            rnd_mat_eff_string += get_industry_text(job)
        elif job.activity_id == 5:
            copying_string += get_industry_text(job)
        elif job.activity_id == 7:
            reverse_eng_string += get_industry_text(job)
        else:
            other_string += get_industry_text(job)
            other_string += f"  Activity: {job.activity_string}\n"

    if manufacturing_string:
        embed.add_field(name="Manufacturing", value=f"```{manufacturing_string}```", inline=False)
    if rnd_time_eff_string:
        embed.add_field(name="R&D Time Eff.", value=f"```{rnd_time_eff_string}```", inline=False)
    if rnd_mat_eff_string:
        embed.add_field(name="R&D Material Eff.", value=f"```{rnd_mat_eff_string}```", inline=False)
    if copying_string:
        embed.add_field(name="Copying", value=f"```{copying_string}```", inline=False)
    if reverse_eng_string:
        embed.add_field(name="Reverse Eng.", value=f"```{reverse_eng_string}```", inline=False)
    if other_string:
        embed.add_field(name="Other", value=f"```{other_string}```", inline=False)

    await context.send(embed=embed)


def get_industry_text(job: IndustryJob) -> str:
    output_string = ""

    output_string += f"{job.product_type.name}\n  Status: {job.status.capitalize()}\n"
    if job.status == "active" and job.end_date > datetime.utcnow():
        output_string += f"  Time Remaining: {get_time_remaining_text(job.end_date - datetime.utcnow())}\n"
    else:
        output_string += f"  Time Remaining: None\n"

    return output_string


def get_time_remaining_text(time: timedelta) -> str:
    output_str = ""

    if time.days:
        if time.days > 1:
            output_str += f"{time.days} days, "
        else:
            output_str += f"{time.days} day, "
    if time.seconds // 3600:
        if time.seconds // 3600 > 1:
            output_str += f"{time.seconds // 3600} hours, "
        else:
            output_str += f"{time.seconds // 3600} hour, "
    if time.seconds % 3600 // 60 > 1:
        output_str += f"{time.seconds % 3600 // 60} minutes."
    else:
        output_str += f"{time.seconds % 3600 // 60} minute."

    return output_str
