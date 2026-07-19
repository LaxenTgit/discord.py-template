import discord
from discord.ext import commands
import os
import json


ACCENT_COLOR = 0x8B5CF6

DATA_FILE = "botdata.json"


def load_data():

    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)



def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )



def set_language(guild_id, language):

    data = load_data()

    guild_data = data.setdefault(
        str(guild_id),
        {}
    )

    guild_data["lang"] = language

    save_data(data)



def get_language(guild_id):

    data = load_data()

    return data.get(
        str(guild_id),
        {}
    ).get(
        "lang",
        "en"
    )



class LanguageView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )


    @discord.ui.button(
        label="Türkçe 🇹🇷",
        style=discord.ButtonStyle.primary,
        custom_id="language_turkish"
    )
    async def turkish(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        set_language(
            interaction.guild.id,
            "tr"
        )


        await interaction.response.send_message(
            "✅ Dil Türkçe olarak ayarlandı.",
            ephemeral=True
        )



    @discord.ui.button(
        label="English 🇬🇧",
        style=discord.ButtonStyle.primary,
        custom_id="language_english"
    )
    async def english(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        set_language(
            interaction.guild.id,
            "en"
        )


        await interaction.response.send_message(
            "✅ Language set to English.",
            ephemeral=True
        )



class LanguageSystem(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    async def send_language_panel(self, guild):

        channel = guild.system_channel


        if channel is None:

            channel = next(
                (
                    c
                    for c in guild.text_channels
                    if c.permissions_for(guild.me).send_messages
                ),
                None
            )


        if channel is None:
            return



        embed = discord.Embed(

            title="🌐 Language Selection",

            description=(

                "Botun hangi dilde konuşmasını istersin?\n\n"

                "Which language should the bot speak?"

            ),

            color=ACCENT_COLOR

        )


        await channel.send(

            embed=embed,

            view=LanguageView()

        )



    @commands.Cog.listener()
    async def on_guild_join(
        self,
        guild
    ):

        await self.send_language_panel(
            guild
        )



    @commands.command(
        name="dil",
        aliases=["language"]
    )

    @commands.has_permissions(
        administrator=True
    )

    async def language_command(
        self,
        ctx
    ):

        embed = discord.Embed(

            title="🌐 Language Selection",

            description=(

                "Botun hangi dilde konuşmasını istersin?\n\n"

                "Which language should the bot speak?"

            ),

            color=ACCENT_COLOR

        )


        await ctx.send(

            embed=embed,

            view=LanguageView()

        )



async def setup(bot):

    await bot.add_cog(
        LanguageSystem(bot)
    )
