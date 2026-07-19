import discord
from discord.ext import commands


ACCENT_COLOR = 0x8B5CF6


class HelpSelect(discord.ui.Select):

    def __init__(self, guild_id, prefix="!"):

        self.guild_id = guild_id
        self.prefix = prefix


        options = [

            discord.SelectOption(
                label="📁 Channel Management",
                value="channels"
            ),

            discord.SelectOption(
                label="🛡️ Moderation",
                value="moderation"
            ),

            discord.SelectOption(
                label="✅ Verification",
                value="verify"
            ),

            discord.SelectOption(
                label="🎫 Tickets",
                value="ticket"
            ),

            discord.SelectOption(
                label="🎭 Roles",
                value="roles"
            ),

            discord.SelectOption(
                label="🔧 General",
                value="general"
            )

        ]


        super().__init__(
            placeholder="Choose a category...",
            options=options,
            min_values=1,
            max_values=1
        )



    async def callback(
        self,
        interaction: discord.Interaction
    ):


        p = self.prefix


        pages = {

            "channels": (

                "📁 **Channel Management**\n\n"

                f"`{p}kanal <text|voice> <name>`\n"
                "Creates a channel\n\n"

                f"`{p}sil <name>`\n"
                "Deletes a channel"

            ),



            "moderation": (

                "🛡️ **Moderation Commands**\n\n"

                f"`{p}mute @user [time] [reason]`\n"
                f"`{p}unmute @user`\n"
                f"`{p}kick @user [reason]`\n"
                f"`{p}ban @user [reason]`\n"
                f"`{p}unban <id>`\n"
                f"`{p}warn @user [reason]`\n"
                f"`{p}warnings @user`\n"
                f"`{p}clear <amount>`"

            ),



            "verify": (

                "✅ **Verification System**\n\n"

                f"`{p}verify-setup @role`\n\n"

                "Creates a verification panel.\n"
                "Users can click the button to receive the role."

            ),



            "ticket": (

                "🎫 **Ticket System**\n\n"

                f"`{p}ticket-setup`\n\n"

                "Creates a support ticket panel."

            ),



            "roles": (

                "🎭 **Role System**\n\n"

                f"`{p}rol-olustur <name> [color]`\n"

                f"`{p}rolmenu @role1 @role2`\n\n"

                "Creates custom roles and self role menus."

            ),



            "general": (

                "🔧 **General Commands**\n\n"

                f"`{p}help`\n"

                f"`{p}ping`\n"

                f"`{p}server`\n"

                f"`{p}kullanici`\n"

                f"`{p}owner`"

            )

        }



        embed = discord.Embed(

            title="⚙️ Command Menu",

            description=pages[self.values[0]],

            color=ACCENT_COLOR

        )


        embed.set_footer(
            text=f"{interaction.client.user.name} • {p}help"
        )


        await interaction.response.edit_message(
            embed=embed
        )




class HelpView(discord.ui.View):

    def __init__(
        self,
        guild_id,
        prefix="!"
    ):

        super().__init__(
            timeout=120
        )


        self.add_item(
            HelpSelect(
                guild_id,
                prefix
            )
        )




class HelpSystem(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot



    @commands.command(
        name="help"
    )

    async def help_command(
        self,
        ctx
    ):


        embed = discord.Embed(

            title="⚙️ Command Menu",

            description=(

                "Choose a category below "
                "to explore commands."

            ),

            color=ACCENT_COLOR

        )


        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )


        embed.set_footer(

            text=f"{self.bot.user.name} • !help"

        )


        await ctx.send(

            embed=embed,

            view=HelpView(
                ctx.guild.id,
                self.bot.command_prefix
            )

        )



async def setup(bot):

    await bot.add_cog(
        HelpSystem(bot)
    )
