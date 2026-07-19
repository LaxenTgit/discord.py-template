import discord
from discord.ext import commands
from datetime import timedelta


ACCENT_COLOR = 0x8B5CF6

open_tickets = {}


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="close_ticket"
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild_id = interaction.guild.id

        await interaction.response.send_message(
            "🔒 This ticket will close in 5 seconds..."
        )

        guild_tickets = open_tickets.get(guild_id, {})

        user_id = next(
            (
                uid
                for uid, channel_id in guild_tickets.items()
                if channel_id == interaction.channel.id
            ),
            None
        )

        if user_id:
            del guild_tickets[user_id]

        await discord.utils.sleep_until(
            discord.utils.utcnow() + timedelta(seconds=5)
        )

        await interaction.channel.delete()


class TicketPanelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="Create Ticket",
        style=discord.ButtonStyle.primary,
        emoji="🎫",
        custom_id="create_ticket"
    )
    async def create(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        user = interaction.user

        guild_id = guild.id


        tickets = open_tickets.setdefault(
            guild_id,
            {}
        )


        existing_ticket = tickets.get(user.id)


        if existing_ticket:

            channel = guild.get_channel(existing_ticket)

            if channel:

                await interaction.response.send_message(
                    f"❌ You already have an open ticket: {channel.mention}",
                    ephemeral=True
                )

                return



        overwrites = {

            guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),


            user:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),


            guild.me:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }


        for role in guild.roles:

            if (
                role.permissions.administrator
                or role.permissions.manage_channels
            ):

                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )


        channel = await guild.create_text_channel(

            name=f"ticket-{user.name}"[:100],

            overwrites=overwrites,

            reason=f"Ticket created by {user}"

        )


        tickets[user.id] = channel.id



        embed = discord.Embed(

            title="🎫 Support Ticket",

            description=(

                f"{user.mention}, your ticket has been created.\n\n"

                "A staff member will help you soon.\n"

                "Click the button below to close this ticket."

            ),

            color=ACCENT_COLOR

        )


        await channel.send(

            embed=embed,

            view=TicketCloseView()

        )


        await interaction.response.send_message(

            f"✅ Your ticket has been created: {channel.mention}",

            ephemeral=True

        )



class TicketSetup(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    @commands.command(
        name="ticket-setup"
    )

    @commands.has_permissions(
        administrator=True
    )

    @commands.bot_has_permissions(
        manage_channels=True
    )

    async def ticket_setup(self, ctx):

        embed = discord.Embed(

            title="🎫 Support Tickets",

            description=(

                "Need help?\n\n"

                "Click the button below to create a private support ticket."

            ),

            color=ACCENT_COLOR

        )


        await ctx.send(

            embed=embed,

            view=TicketPanelView()

        )



async def setup(bot):

    await bot.add_cog(
        TicketSetup(bot)
    )
