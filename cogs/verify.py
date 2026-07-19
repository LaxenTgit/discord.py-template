import discord
from discord.ext import commands


ACCENT_COLOR = 0x8B5CF6


class VerifyView(discord.ui.View):

    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

        self.verify.custom_id = f"verify_{role_id}"


    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="verify_button"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = interaction.guild.get_role(
            self.role_id
        )


        if role is None:

            await interaction.response.send_message(
                "❌ Verification role no longer exists.",
                ephemeral=True
            )

            return



        if role in interaction.user.roles:

            await interaction.response.send_message(
                "✅ You are already verified.",
                ephemeral=True
            )

            return



        await interaction.user.add_roles(
            role,
            reason="Verification System"
        )


        await interaction.response.send_message(
            "✅ Verification successful! Welcome to the server.",
            ephemeral=True
        )



class VerifySystem(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    @commands.command(
        name="verify-setup"
    )

    @commands.has_permissions(
        administrator=True
    )

    @commands.bot_has_permissions(
        manage_roles=True
    )

    async def verify_setup(
        self,
        ctx,
        role: discord.Role = None
    ):


        if role is None:

            await ctx.send(
                "❌ Usage: `!verify-setup @role`"
            )

            return



        embed = discord.Embed(

            title="✅ Welcome to the Server!",

            description=(

                "Click the button below to verify "
                "and unlock access to the server."

            ),

            color=ACCENT_COLOR

        )


        view = VerifyView(
            role.id
        )


        await ctx.send(
            embed=embed,
            view=view
        )


        self.bot.add_view(
            view
        )



async def setup(bot):

    await bot.add_cog(
        VerifySystem(bot)
    )
