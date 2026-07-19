import discord
from discord.ext import commands
from datetime import timedelta
import re


ACCENT_COLOR = 0x8B5CF6


warnings_db = {}



def parse_duration(duration):

    match = re.match(
        r"^(\d+)([smhd])$",
        duration.lower()
    )


    if not match:
        return None


    amount = int(match.group(1))
    unit = match.group(2)


    units = {

        "s": "seconds",
        "m": "minutes",
        "h": "hours",
        "d": "days"

    }


    return timedelta(
        **{
            units[unit]: amount
        }
    )



class Moderation(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    @commands.bot_has_permissions(
        moderate_members=True
    )
    async def mute(
        self,
        ctx,
        member: discord.Member,
        duration="10m",
        *,
        reason=None
    ):

        reason = reason or "No reason provided"


        time = parse_duration(
            duration
        )


        if time is None:

            await ctx.send(
                "❌ Invalid duration. Example: `10m`, `2h`, `1d`"
            )

            return



        if time > timedelta(days=28):

            await ctx.send(
                "❌ Maximum timeout duration is 28 days."
            )

            return



        await member.timeout(
            time,
            reason=reason
        )


        embed = discord.Embed(

            title="🔇 Member Muted",

            description=f"{member.mention} has been muted.",

            color=ACCENT_COLOR

        )


        embed.add_field(
            name="Duration",
            value=duration
        )


        embed.add_field(
            name="Moderator",
            value=ctx.author.mention
        )


        embed.add_field(
            name="Reason",
            value=reason
        )


        await ctx.send(
            embed=embed
        )




    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def unmute(
        self,
        ctx,
        member: discord.Member
    ):


        await member.timeout(
            None,
            reason=f"Unmuted by {ctx.author}"
        )


        await ctx.send(
            f"🔊 {member.mention} has been unmuted."
        )




    @commands.command()
    @commands.has_permissions(
        kick_members=True
    )
    @commands.bot_has_permissions(
        kick_members=True
    )
    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason=None
    ):


        reason = reason or "No reason provided"


        await member.kick(
            reason=reason
        )


        embed = discord.Embed(

            title="👢 Member Kicked",

            description=(

                f"{member.mention} was kicked.\n\n"

                f"Reason: {reason}"

            ),

            color=ACCENT_COLOR

        )


        await ctx.send(
            embed=embed
        )




    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    @commands.bot_has_permissions(
        ban_members=True
    )
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason=None
    ):


        reason = reason or "No reason provided"


        await member.ban(
            reason=reason
        )


        embed = discord.Embed(

            title="🔨 Member Banned",

            description=(

                f"{member.mention} was banned.\n\n"

                f"Reason: {reason}"

            ),

            color=ACCENT_COLOR

        )


        await ctx.send(
            embed=embed
        )




    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    async def unban(
        self,
        ctx,
        user_id: int
    ):


        user = discord.Object(
            id=user_id
        )


        try:

            await ctx.guild.unban(
                user
            )


            await ctx.send(
                f"✅ User `{user_id}` has been unbanned."
            )


        except discord.NotFound:

            await ctx.send(
                "❌ User not found in ban list."
            )




    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def warn(
        self,
        ctx,
        member: discord.Member,
        *,
        reason=None
    ):


        reason = reason or "No reason provided"


        guild_warns = warnings_db.setdefault(
            ctx.guild.id,
            {}
        )


        user_warns = guild_warns.setdefault(
            member.id,
            []
        )


        user_warns.append(
            reason
        )


        embed = discord.Embed(

            title="⚠️ Warning Issued",

            description=(

                f"{member.mention} received a warning.\n"

                f"Total warnings: {len(user_warns)}"

            ),

            color=ACCENT_COLOR

        )


        embed.add_field(
            name="Reason",
            value=reason
        )


        await ctx.send(
            embed=embed
        )




    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def warnings(
        self,
        ctx,
        member: discord.Member
    ):


        warns = warnings_db.get(
            ctx.guild.id,
            {}
        ).get(
            member.id,
            []
        )


        if not warns:

            await ctx.send(
                f"✅ {member.mention} has no warnings."
            )

            return



        embed = discord.Embed(

            title=f"⚠️ {member.display_name}'s Warnings",

            description="\n".join(

                f"`{i+1}.` {warn}"

                for i, warn in enumerate(warns)

            ),

            color=ACCENT_COLOR

        )


        await ctx.send(
            embed=embed
        )




    @commands.command()
    @commands.has_permissions(
        manage_messages=True
    )
    @commands.bot_has_permissions(
        manage_messages=True
    )
    async def clear(
        self,
        ctx,
        amount: int
    ):


        if amount < 1 or amount > 100:

            await ctx.send(
                "❌ Amount must be between 1 and 100."
            )

            return



        deleted = await ctx.channel.purge(
            limit=amount + 1
        )


        msg = await ctx.send(
            f"🧹 {len(deleted)-1} messages deleted."
        )


        await msg.delete(
            delay=3
        )



async def setup(bot):

    await bot.add_cog(
        Moderation(bot)
    )
