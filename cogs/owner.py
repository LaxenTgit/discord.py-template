import discord
from discord.ext import commands


ACCENT_COLOR = 0x8B5CF6


OWNER_ID = 1487413399653716048



class OwnerSystem(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    @commands.command(
        name="owner"
    )
    async def owner_info(
        self,
        ctx
    ):


        embed = discord.Embed(

            title="👑 Bot Owner",

            description=(

                f"Bot owner: **<@{OWNER_ID}>**\n\n"

                f"**Discord ID:** `{OWNER_ID}`"

            ),

            color=ACCENT_COLOR

        )


        embed.set_thumbnail(

            url=self.bot.user.display_avatar.url

        )


        embed.add_field(

            name="Want this bot for free?",

            value=(

                f"[Click here]"
                f"(https://discord.com/users/{OWNER_ID})"

            ),

            inline=False

        )


        embed.set_footer(

            text=f"{self.bot.user.name} • !help & !owner"

        )


        await ctx.send(

            embed=embed

        )



async def setup(bot):

    await bot.add_cog(
        OwnerSystem(bot)
    )
