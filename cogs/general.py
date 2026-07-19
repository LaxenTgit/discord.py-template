import discord
from discord.ext import commands
import time

from utils.config import ACCENT_COLOR, PREFIX
from utils.lang import t


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def ping(self, ctx):

        start = time.monotonic()

        msg = await ctx.send(
            t(ctx.guild.id, "ping_measuring")
        )

        elapsed = (time.monotonic() - start) * 1000


        embed = discord.Embed(
            title=t(ctx.guild.id, "ping_title"),
            description=t(
                ctx.guild.id,
                "ping_desc",
                api=f"{self.bot.latency * 1000:.0f}",
                msg=f"{elapsed:.0f}"
            ),
            color=ACCENT_COLOR
        )

        await msg.edit(
            content=None,
            embed=embed
        )


    @commands.command(name="server")
    async def server_info(self, ctx):

        guild = ctx.guild
        gid = guild.id


        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=ACCENT_COLOR
        )


        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )


        embed.add_field(
            name=t(gid, "server_owner"),
            value=guild.owner.mention if guild.owner else t(gid, "server_unknown"),
            inline=True
        )

        embed.add_field(
            name=t(gid, "server_members"),
            value=guild.member_count,
            inline=True
        )

        embed.add_field(
            name=t(gid, "server_channels"),
            value=len(guild.channels),
            inline=True
        )

        embed.add_field(
            name=t(gid, "server_roles"),
            value=len(guild.roles),
            inline=True
        )

        embed.add_field(
            name=t(gid, "server_created"),
            value=discord.utils.format_dt(
                guild.created_at,
                "D"
            ),
            inline=True
        )


        await ctx.send(embed=embed)



    @commands.command(name="kullanici")
    async def user_info(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author
        gid = ctx.guild.id


        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=ACCENT_COLOR
        )


        embed.set_thumbnail(
            url=member.display_avatar.url
        )


        embed.add_field(
            name=t(gid, "user_username"),
            value=str(member),
            inline=True
        )

        embed.add_field(
            name=t(gid, "user_id"),
            value=member.id,
            inline=True
        )

        embed.add_field(
            name=t(gid, "user_joined"),
            value=discord.utils.format_dt(
                member.joined_at,
                "D"
            ),
            inline=True
        )

        embed.add_field(
            name=t(gid, "user_created"),
            value=discord.utils.format_dt(
                member.created_at,
                "D"
            ),
            inline=True
        )


        top_role = (
            member.top_role.mention
            if member.top_role.name != "@everyone"
            else t(gid, "user_no_role")
        )


        embed.add_field(
            name=t(gid, "user_top_role"),
            value=top_role,
            inline=True
        )


        await ctx.send(embed=embed)



    @commands.command(name="owner")
    async def owner_info(self, ctx):

        owner_id = 1487413399653716048


        embed = discord.Embed(
            title="👑 Bot Owner",
            description=(
                f"Bot owner: **<@{owner_id}>**\n\n"
                f"**Discord ID:** `{owner_id}`"
            ),
            color=ACCENT_COLOR
        )


        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )


        embed.add_field(
            name="Want this bot for free?",
            value=f"[Click here](https://discord.com/users/{owner_id})",
            inline=False
        )


        embed.set_footer(
            text=f"{self.bot.user.name} • !help & !owner"
        )


        await ctx.send(embed=embed)



async def setup(bot):

    await bot.add_cog(
        General(bot)
    )
