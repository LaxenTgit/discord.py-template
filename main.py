import discord
from discord.ext import commands
from datetime import timedelta
import os
import re
import json
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

ACCENT_COLOR = 0x8B5CF6
DATA_FILE = "botdata.json"


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_guild_data(guild_id: int) -> dict:
    data = load_data()
    return data.setdefault(str(guild_id), {})


def set_guild_data(guild_id: int, key: str, value):
    data = load_data()
    guild_data = data.setdefault(str(guild_id), {})
    guild_data[key] = value
    save_data(data)


def get_lang(guild_id: int) -> str:
    return get_guild_data(guild_id).get("lang", "tr")


T = {
    "lang_prompt_title": {"tr": "🌐 Dil Seçimi / Language Selection",
                           "en": "🌐 Dil Seçimi / Language Selection"},
    "lang_prompt_desc": {"tr": "Botun hangi dilde konuşmasını istersin?\nWhich language should the bot speak?",
                          "en": "Botun hangi dilde konuşmasını istersin?\nWhich language should the bot speak?"},
    "lang_set": {"tr": "✅ Dil **Türkçe** olarak ayarlandı. Artık tüm komutlar Türkçe olacak.",
                 "en": "✅ Language set to **English**. All commands will now respond in English."},

    "channel_created_text": {"tr": "✅ `{name}` adlı metin kanalı oluşturuldu.", "en": "✅ Text channel `{name}` created."},
    "channel_created_voice": {"tr": "✅ `{name}` adlı ses kanalı oluşturuldu.", "en": "✅ Voice channel `{name}` created."},
    "channel_invalid_type": {"tr": "❌ Geçersiz kanal türü. Kullanım: `{p}kanal <text|voice> <isim>`",
                              "en": "❌ Invalid channel type. Usage: `{p}kanal <text|voice> <name>`"},
    "channel_not_found": {"tr": "❌ `{name}` adlı kanal bulunamadı.", "en": "❌ Channel `{name}` not found."},
    "channel_deleted": {"tr": "🗑️ `{name}` adlı kanal silindi.", "en": "🗑️ Channel `{name}` deleted."},

    "mute_invalid_duration": {"tr": "❌ Geçersiz süre formatı. Örnek: `10m`, `2h`, `1d`",
                               "en": "❌ Invalid duration format. Example: `10m`, `2h`, `1d`"},
    "mute_max_duration": {"tr": "❌ Discord en fazla 28 günlük timeout izni veriyor.",
                           "en": "❌ Discord only allows timeouts up to 28 days."},
    "mute_title": {"tr": "🔇 Üye Susturuldu", "en": "🔇 Member Muted"},
    "mute_desc": {"tr": "{member} susturuldu.", "en": "{member} has been muted."},
    "mute_field_duration": {"tr": "Süre", "en": "Duration"},
    "mute_field_mod": {"tr": "Yetkili", "en": "Moderator"},
    "mute_field_reason": {"tr": "Sebep", "en": "Reason"},
    "mute_dm": {"tr": "🔇 **{guild}** sunucusunda {duration} süreyle susturuldun.\nSebep: {reason}",
                "en": "🔇 You have been muted in **{guild}** for {duration}.\nReason: {reason}"},
    "unmute_not_muted": {"tr": "❌ Bu üye zaten susturulmuş değil.", "en": "❌ This member is not currently muted."},
    "unmute_success": {"tr": "🔊 {member} kullanıcısının susturması kaldırıldı.", "en": "🔊 {member} has been unmuted."},

    "kick_title": {"tr": "👢 Üye Sunucudan Atıldı", "en": "👢 Member Kicked"},
    "kick_desc": {"tr": "{member} sunucudan atıldı.\n**Sebep:** {reason}", "en": "{member} was kicked.\n**Reason:** {reason}"},
    "ban_title": {"tr": "🔨 Üye Yasaklandı", "en": "🔨 Member Banned"},
    "ban_desc": {"tr": "{member} sunucudan yasaklandı.\n**Sebep:** {reason}", "en": "{member} was banned.\n**Reason:** {reason}"},
    "unban_success": {"tr": "✅ `{id}` ID'li kullanıcının yasağı kaldırıldı.", "en": "✅ User with ID `{id}` has been unbanned."},
    "unban_not_found": {"tr": "❌ Bu ID'ye sahip yasaklı bir kullanıcı bulunamadı.", "en": "❌ No banned user found with that ID."},

    "warn_title": {"tr": "⚠️ Uyarı Verildi", "en": "⚠️ Warning Issued"},
    "warn_desc": {"tr": "{member} uyarıldı. (Toplam uyarı: {count})", "en": "{member} has been warned. (Total warnings: {count})"},
    "warn_none": {"tr": "✅ {member} kullanıcısının hiç uyarısı yok.", "en": "✅ {member} has no warnings."},
    "warn_history_title": {"tr": "⚠️ {member} — Uyarı Geçmişi", "en": "⚠️ {member} — Warning History"},

    "clear_invalid_range": {"tr": "❌ 1 ile 100 arasında bir sayı gir.", "en": "❌ Enter a number between 1 and 100."},
    "clear_success": {"tr": "🧹 {count} mesaj silindi.", "en": "🧹 {count} messages deleted."},

    "ping_title": {"tr": "🏓 Pong!", "en": "🏓 Pong!"},
    "ping_desc": {"tr": "**API Gecikmesi:** {api}ms\n**Mesaj Gecikmesi:** {msg}ms",
                  "en": "**API Latency:** {api}ms\n**Message Latency:** {msg}ms"},
    "ping_measuring": {"tr": "🏓 Ölçülüyor...", "en": "🏓 Measuring..."},

    "server_owner": {"tr": "Sahip", "en": "Owner"},
    "server_members": {"tr": "Üye Sayısı", "en": "Members"},
    "server_channels": {"tr": "Kanal Sayısı", "en": "Channels"},
    "server_roles": {"tr": "Rol Sayısı", "en": "Roles"},
    "server_created": {"tr": "Oluşturulma Tarihi", "en": "Created On"},
    "server_unknown": {"tr": "Bilinmiyor", "en": "Unknown"},

    "user_username": {"tr": "Kullanıcı Adı", "en": "Username"},
    "user_id": {"tr": "ID", "en": "ID"},
    "user_joined": {"tr": "Sunucuya Katılma", "en": "Joined Server"},
    "user_created": {"tr": "Hesap Oluşturulma", "en": "Account Created"},
    "user_top_role": {"tr": "En Üst Rol", "en": "Top Role"},
    "user_no_role": {"tr": "Yok", "en": "None"},

    "verify_no_role_arg": {"tr": "❌ Kullanım: `{p}verify-setup @rol`", "en": "❌ Usage: `{p}verify-setup @role`"},
    "verify_setup_success": {"tr": "✅ Doğrulama paneli kuruldu.", "en": "✅ Verification panel has been set up."},
    "verify_panel_title": {"tr": "✅ Sunucuya Hoş Geldin!", "en": "✅ Welcome to the Server!"},
    "verify_panel_desc": {"tr": "Sunucunun tüm kanallarına erişmek için aşağıdaki butona tıklayarak doğrulama yap.",
                           "en": "Click the button below to verify and unlock access to the server."},
    "verify_button_label": {"tr": "Doğrula", "en": "Verify"},
    "verify_already": {"tr": "✅ Zaten doğrulanmışsın.", "en": "✅ You are already verified."},
    "verify_success": {"tr": "✅ Doğrulama başarılı! Sunucuya hoş geldin.", "en": "✅ Verification successful! Welcome to the server."},
    "verify_role_missing": {"tr": "❌ Doğrulama rolü artık mevcut değil, bir yetkiliye bildir.",
                             "en": "❌ The verification role no longer exists, please notify a staff member."},

    "ticket_setup_success": {"tr": "✅ Destek talebi paneli kuruldu.", "en": "✅ Ticket panel has been set up."},
    "ticket_panel_title": {"tr": "🎫 Destek Talebi", "en": "🎫 Support Tickets"},
    "ticket_panel_desc": {"tr": "Yardıma mı ihtiyacın var? Aşağıdaki butona tıklayarak özel bir destek kanalı aç.",
                           "en": "Need help? Click the button below to open a private support channel."},
    "ticket_button_label": {"tr": "Talep Oluştur", "en": "Create Ticket"},
    "ticket_already_open": {"tr": "❌ Zaten açık bir talebin var: {channel}", "en": "❌ You already have an open ticket: {channel}"},
    "ticket_created": {"tr": "✅ Talebin oluşturuldu: {channel}", "en": "✅ Your ticket has been created: {channel}"},
    "ticket_welcome_title": {"tr": "🎫 Destek Talebi", "en": "🎫 Support Ticket"},
    "ticket_welcome_desc": {"tr": "{member}, talebini açtın. Bir yetkili en kısa sürede seninle ilgilenecek.\nKapatmak için aşağıdaki butona tıklayabilirsin.",
                             "en": "{member}, your ticket has been opened. Staff will assist you shortly.\nClick the button below to close it."},
    "ticket_close_label": {"tr": "Talebi Kapat", "en": "Close Ticket"},
    "ticket_closing": {"tr": "🔒 Bu talep 5 saniye içinde kapatılacak...", "en": "🔒 This ticket will close in 5 seconds..."},

    "role_create_success": {"tr": "✅ `{name}` rolü oluşturuldu.", "en": "✅ Role `{name}` has been created."},
    "role_create_usage": {"tr": "❌ Kullanım: `{p}rol-olustur <isim> [#renkkodu]`", "en": "❌ Usage: `{p}rol-olustur <name> [#colorcode]`"},
    "role_create_bad_color": {"tr": "❌ Geçersiz renk kodu. Örnek: `#8B5CF6`", "en": "❌ Invalid color code. Example: `#8B5CF6`"},

    "rolemenu_usage": {"tr": "❌ Kullanım: `{p}rolmenu @rol1 @rol2 ...` (en az 1, en fazla 25 rol)",
                        "en": "❌ Usage: `{p}rolmenu @role1 @role2 ...` (1 to 25 roles)"},
    "rolemenu_setup_success": {"tr": "✅ Rol seçim paneli kuruldu.", "en": "✅ Role selection panel has been set up."},
    "rolemenu_panel_title": {"tr": "🎭 Rol Seçimi", "en": "🎭 Role Selection"},
    "rolemenu_panel_desc": {"tr": "Aşağıdaki menüden istediğin rolleri seç. Tekrar seçerek kaldırabilirsin.",
                             "en": "Pick your roles from the menu below. Select again to remove them."},
    "rolemenu_placeholder": {"tr": "Rollerini seç...", "en": "Select your roles..."},
    "rolemenu_updated": {"tr": "✅ Rollerin güncellendi.", "en": "✅ Your roles have been updated."},

    "err_missing_perms": {"tr": "❌ Bu komutu kullanmak için yetkin yok.", "en": "❌ You don't have permission to use this command."},
    "err_bot_missing_perms": {"tr": "❌ Botun bu işlemi yapabilmek için yetkisi yok.", "en": "❌ The bot lacks permission to do this."},
    "err_missing_arg": {"tr": "❌ Eksik argüman. Kullanım: `{p}help` ile kontrol edebilirsin.",
                         "en": "❌ Missing argument. Check `{p}help` for usage."},
    "err_bad_arg": {"tr": "❌ Geçersiz argüman girdin.", "en": "❌ Invalid argument provided."},
    "err_member_not_found": {"tr": "❌ Böyle bir üye bulunamadı.", "en": "❌ Member not found."},
    "err_cooldown": {"tr": "⏳ Bu komut şu an bekleme süresinde. {s:.1f} saniye sonra tekrar dene.",
                      "en": "⏳ This command is on cooldown. Try again in {s:.1f}s."},
    "err_unexpected": {"tr": "❌ Beklenmeyen bir hata oluştu.", "en": "❌ An unexpected error occurred."},

    "help_title": {"tr": "⚙️ Komut Menüsü", "en": "⚙️ Command Menu"},
    "help_desc": {"tr": "Aşağıdaki menüden bir kategori seç ve komutları keşfet.",
                  "en": "Pick a category from the menu below to explore commands."},
    "help_placeholder": {"tr": "Bir kategori seç...", "en": "Choose a category..."},
    "cat_channels": {"tr": "📁 Kanal Yönetimi", "en": "📁 Channel Management"},
    "cat_mod": {"tr": "🛡️ Moderasyon", "en": "🛡️ Moderation"},
    "cat_verify": {"tr": "✅ Doğrulama", "en": "✅ Verification"},
    "cat_ticket": {"tr": "🎫 Destek Talebi", "en": "🎫 Tickets"},
    "cat_roles": {"tr": "🎭 Rol Sistemi", "en": "🎭 Role System"},
    "cat_general": {"tr": "🔧 Genel", "en": "🔧 General"},
}


def t(guild_id: int, key: str, **kwargs) -> str:
    lang = get_lang(guild_id)
    template = T[key][lang]
    return template.format(p=PREFIX, **kwargs) if kwargs or "{p}" in template else template.format(p=PREFIX)


def parse_duration(duration_str: str) -> timedelta | None:
    match = re.match(r"^(\d+)([smhd])$", duration_str.lower())
    if not match:
        return None
    amount, unit = int(match.group(1)), match.group(2)
    unit_map = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
    return timedelta(**{unit_map[unit]: amount})


warnings_db = {}
open_tickets = {}


class LanguageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Türkçe 🇹🇷", style=discord.ButtonStyle.primary, custom_id="lang_tr")
    async def turkish(self, interaction: discord.Interaction, button: discord.ui.Button):
        set_guild_data(interaction.guild.id, "lang", "tr")
        await interaction.response.send_message(t(interaction.guild.id, "lang_set"), ephemeral=True)

    @discord.ui.button(label="English 🇬🇧", style=discord.ButtonStyle.primary, custom_id="lang_en")
    async def english(self, interaction: discord.Interaction, button: discord.ui.Button):
        set_guild_data(interaction.guild.id, "lang", "en")
        await interaction.response.send_message(t(interaction.guild.id, "lang_set"), ephemeral=True)


@bot.event
async def on_guild_join(guild: discord.Guild):
    target = guild.system_channel
    if target is None or not target.permissions_for(guild.me).send_messages:
        target = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
    if target is None:
        return

    embed = discord.Embed(
        title="🌐 Dil Seçimi / Language Selection",
        description="Botun hangi dilde konuşmasını istersin?\nWhich language should the bot speak?",
        color=ACCENT_COLOR
    )
    await target.send(embed=embed, view=LanguageView())


@bot.command(name="dil", aliases=["language"])
@commands.has_permissions(administrator=True)
async def dil(ctx):
    embed = discord.Embed(
        title="🌐 Dil Seçimi / Language Selection",
        description="Botun hangi dilde konuşmasını istersin?\nWhich language should the bot speak?",
        color=ACCENT_COLOR
    )
    await ctx.send(embed=embed, view=LanguageView())


@bot.event
async def on_ready():
    print(f"✅ {bot.user} olarak başarıyla bağlandı")
    print(f"📡 {len(bot.guilds)} sunucuda aktif")

    bot.add_view(LanguageView())
    bot.add_view(TicketPanelView())
    bot.add_view(TicketCloseView())

    data = load_data()
    for guild_id_str, gdata in data.items():
        if gdata.get("verify_role_id"):
            bot.add_view(VerifyView(gdata["verify_role_id"]))
        if gdata.get("selfroles"):
            view = discord.ui.View(timeout=None)
            view.add_item(RoleMenuSelect(gdata["selfroles"]))
            bot.add_view(view)

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{PREFIX}help & {PREFIX}owner")
    )


@bot.event
async def on_command_error(ctx, error):
    gid = ctx.guild.id if ctx.guild else 0

    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(t(gid, "err_missing_perms"))
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(t(gid, "err_bot_missing_perms"))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(t(gid, "err_missing_arg"))
    elif isinstance(error, commands.BadArgument):
        await ctx.send(t(gid, "err_bad_arg"))
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(t(gid, "err_member_not_found"))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(t(gid, "err_cooldown", s=error.retry_after))
    else:
        await ctx.send(t(gid, "err_unexpected"))
        raise error


@bot.command()
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def kanal(ctx, tur: str, *, isim: str):
    tur = tur.lower()
    if tur in ("text", "metin"):
        channel = await ctx.guild.create_text_channel(name=isim)
        await ctx.send(t(ctx.guild.id, "channel_created_text", name=channel.name))
    elif tur in ("voice", "ses"):
        channel = await ctx.guild.create_voice_channel(name=isim)
        await ctx.send(t(ctx.guild.id, "channel_created_voice", name=channel.name))
    else:
        await ctx.send(t(ctx.guild.id, "channel_invalid_type"))


@bot.command()
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def sil(ctx, *, isim: str):
    channel = discord.utils.get(ctx.guild.channels, name=isim)
    if channel is None:
        await ctx.send(t(ctx.guild.id, "channel_not_found", name=isim))
        return
    await channel.delete()
    await ctx.send(t(ctx.guild.id, "channel_deleted", name=isim))


@bot.command()
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: str = "10m", *, sebep: str = None):
    reason = sebep or ("Sebep belirtilmedi" if get_lang(ctx.guild.id) == "tr" else "No reason provided")
    delta = parse_duration(duration)
    if delta is None:
        await ctx.send(t(ctx.guild.id, "mute_invalid_duration"))
        return
    if delta > timedelta(days=28):
        await ctx.send(t(ctx.guild.id, "mute_max_duration"))
        return

    await member.timeout(delta, reason=f"{ctx.author}: {reason}")

    embed = discord.Embed(title=t(ctx.guild.id, "mute_title"), color=ACCENT_COLOR,
                           description=t(ctx.guild.id, "mute_desc", member=member.mention))
    embed.add_field(name=t(ctx.guild.id, "mute_field_duration"), value=duration, inline=True)
    embed.add_field(name=t(ctx.guild.id, "mute_field_mod"), value=ctx.author.mention, inline=True)
    embed.add_field(name=t(ctx.guild.id, "mute_field_reason"), value=reason, inline=False)
    await ctx.send(embed=embed)

    try:
        await member.send(t(ctx.guild.id, "mute_dm", guild=ctx.guild.name, duration=duration, reason=reason))
    except discord.Forbidden:
        pass


@bot.command()
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    if member.timed_out_until is None:
        await ctx.send(t(ctx.guild.id, "unmute_not_muted"))
        return
    await member.timeout(None, reason=f"Unmuted by {ctx.author}")
    await ctx.send(t(ctx.guild.id, "unmute_success", member=member.mention))


@bot.command()
@commands.has_permissions(kick_members=True)
@commands.bot_has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep: str = None):
    reason = sebep or ("Sebep belirtilmedi" if get_lang(ctx.guild.id) == "tr" else "No reason provided")
    await member.kick(reason=f"{ctx.author}: {reason}")
    embed = discord.Embed(title=t(ctx.guild.id, "kick_title"), color=ACCENT_COLOR,
                           description=t(ctx.guild.id, "kick_desc", member=member.mention, reason=reason))
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep: str = None):
    reason = sebep or ("Sebep belirtilmedi" if get_lang(ctx.guild.id) == "tr" else "No reason provided")
    await member.ban(reason=f"{ctx.author}: {reason}")
    embed = discord.Embed(title=t(ctx.guild.id, "ban_title"), color=ACCENT_COLOR,
                           description=t(ctx.guild.id, "ban_desc", member=member.mention, reason=reason))
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = discord.Object(id=user_id)
    try:
        await ctx.guild.unban(user)
        await ctx.send(t(ctx.guild.id, "unban_success", id=user_id))
    except discord.NotFound:
        await ctx.send(t(ctx.guild.id, "unban_not_found"))


@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, sebep: str = None):
    reason = sebep or ("Sebep belirtilmedi" if get_lang(ctx.guild.id) == "tr" else "No reason provided")
    guild_warns = warnings_db.setdefault(ctx.guild.id, {})
    user_warns = guild_warns.setdefault(member.id, [])
    user_warns.append(reason)

    embed = discord.Embed(title=t(ctx.guild.id, "warn_title"), color=ACCENT_COLOR,
                           description=t(ctx.guild.id, "warn_desc", member=member.mention, count=len(user_warns)))
    embed.add_field(name=t(ctx.guild.id, "mute_field_reason"), value=reason, inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def warnings(ctx, member: discord.Member):
    user_warns = warnings_db.get(ctx.guild.id, {}).get(member.id, [])
    if not user_warns:
        await ctx.send(t(ctx.guild.id, "warn_none", member=member.mention))
        return
    embed = discord.Embed(
        title=t(ctx.guild.id, "warn_history_title", member=member.display_name),
        color=ACCENT_COLOR,
        description="\n".join(f"`{i+1}.` {r}" for i, r in enumerate(user_warns))
    )
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def clear(ctx, adet: int):
    if adet < 1 or adet > 100:
        await ctx.send(t(ctx.guild.id, "clear_invalid_range"))
        return
    deleted = await ctx.channel.purge(limit=adet + 1)
    msg = await ctx.send(t(ctx.guild.id, "clear_success", count=len(deleted) - 1))
    await msg.delete(delay=3)


class VerifyView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id
        self.verify.custom_id = f"verify_{role_id}"

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            await interaction.response.send_message(t(interaction.guild.id, "verify_role_missing"), ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message(t(interaction.guild.id, "verify_already"), ephemeral=True)
            return
        await interaction.user.add_roles(role, reason="Verify sistemi")
        await interaction.response.send_message(t(interaction.guild.id, "verify_success"), ephemeral=True)


@bot.command(name="verify-setup")
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_roles=True)
async def verify_setup(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(t(ctx.guild.id, "verify_no_role_arg"))
        return

    set_guild_data(ctx.guild.id, "verify_role_id", role.id)

    embed = discord.Embed(
        title=t(ctx.guild.id, "verify_panel_title"),
        description=t(ctx.guild.id, "verify_panel_desc"),
        color=ACCENT_COLOR
    )
    view = VerifyView(role.id)
    await ctx.send(embed=embed, view=view)
    bot.add_view(view)


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = interaction.guild.id
        await interaction.response.send_message(t(gid, "ticket_closing"))

        guild_tickets = open_tickets.get(gid, {})
        uid_to_remove = next((uid for uid, cid in guild_tickets.items() if cid == interaction.channel.id), None)
        if uid_to_remove:
            del guild_tickets[uid_to_remove]

        await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=5))
        await interaction.channel.delete()


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="create_ticket")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        gid = guild.id
        user = interaction.user

        guild_tickets = open_tickets.setdefault(gid, {})
        existing_id = guild_tickets.get(user.id)
        if existing_id:
            existing_channel = guild.get_channel(existing_id)
            if existing_channel:
                await interaction.response.send_message(
                    t(gid, "ticket_already_open", channel=existing_channel.mention), ephemeral=True
                )
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        for role in guild.roles:
            if role.permissions.administrator or role.permissions.manage_channels:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}"[:100],
            overwrites=overwrites,
            reason=f"Ticket - {user}"
        )
        guild_tickets[user.id] = channel.id

        embed = discord.Embed(
            title=t(gid, "ticket_welcome_title"),
            description=t(gid, "ticket_welcome_desc", member=user.mention),
            color=ACCENT_COLOR
        )
        await channel.send(embed=embed, view=TicketCloseView())
        await interaction.response.send_message(t(gid, "ticket_created", channel=channel.mention), ephemeral=True)


@bot.command(name="ticket-setup")
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_channels=True)
async def ticket_setup(ctx):
    embed = discord.Embed(
        title=t(ctx.guild.id, "ticket_panel_title"),
        description=t(ctx.guild.id, "ticket_panel_desc"),
        color=ACCENT_COLOR
    )
    await ctx.send(embed=embed, view=TicketPanelView())


@bot.command(name="rol-olustur")
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def rol_olustur(ctx, isim: str, renk: str = None):
    color = discord.Color(ACCENT_COLOR)
    if renk:
        try:
            color = discord.Color(int(renk.lstrip("#"), 16))
        except ValueError:
            await ctx.send(t(ctx.guild.id, "role_create_bad_color"))
            return

    role = await ctx.guild.create_role(name=isim, color=color, reason=f"{ctx.author} tarafından oluşturuldu")
    await ctx.send(t(ctx.guild.id, "role_create_success", name=role.name))


class RoleMenuSelect(discord.ui.Select):
    def __init__(self, role_ids: list[int], role_names: dict[int, str] = None):
        role_names = role_names or {}
        options = [
            discord.SelectOption(label=role_names.get(rid, str(rid)), value=str(rid))
            for rid in role_ids[:25]
        ]
        super().__init__(
            placeholder="Select your roles...",
            min_values=0,
            max_values=len(options) if options else 1,
            options=options,
            custom_id="rolemenu_select"
        )
        self.role_ids = role_ids

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        selected_ids = {int(v) for v in self.values}

        for rid in self.role_ids:
            role = guild.get_role(rid)
            if role is None:
                continue
            if rid in selected_ids and role not in member.roles:
                await member.add_roles(role)
            elif rid not in selected_ids and role in member.roles:
                await member.remove_roles(role)

        await interaction.response.send_message(t(guild.id, "rolemenu_updated"), ephemeral=True)


@bot.command(name="rolmenu")
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def rolmenu(ctx, roles: commands.Greedy[discord.Role]):
    if not roles or len(roles) > 25:
        await ctx.send(t(ctx.guild.id, "rolemenu_usage"))
        return

    role_ids = [r.id for r in roles]
    role_names = {r.id: r.name for r in roles}
    set_guild_data(ctx.guild.id, "selfroles", role_ids)

    select = RoleMenuSelect(role_ids, role_names)
    select.placeholder = t(ctx.guild.id, "rolemenu_placeholder")

    view = discord.ui.View(timeout=None)
    view.add_item(select)

    embed = discord.Embed(
        title=t(ctx.guild.id, "rolemenu_panel_title"),
        description=t(ctx.guild.id, "rolemenu_panel_desc"),
        color=ACCENT_COLOR
    )
    await ctx.send(embed=embed, view=view)
    bot.add_view(view)


class HelpSelect(discord.ui.Select):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label=t(guild_id, "cat_channels"), value="channels", emoji="📁"),
            discord.SelectOption(label=t(guild_id, "cat_mod"), value="mod", emoji="🛡️"),
            discord.SelectOption(label=t(guild_id, "cat_verify"), value="verify", emoji="✅"),
            discord.SelectOption(label=t(guild_id, "cat_ticket"), value="ticket", emoji="🎫"),
            discord.SelectOption(label=t(guild_id, "cat_roles"), value="roles", emoji="🎭"),
            discord.SelectOption(label=t(guild_id, "cat_general"), value="general", emoji="🔧"),
        ]
        super().__init__(placeholder=t(guild_id, "help_placeholder"), options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        gid = interaction.guild.id
        lang_tr = get_lang(gid) == "tr"
        content = {
            "channels": (
                f"{t(gid, 'cat_channels')}\n\n"
                f"`{PREFIX}kanal <text|voice> <isim>`\n"
                + ("↳ Kanal oluşturur\n\n" if lang_tr else "↳ Creates a channel\n\n")
                + f"`{PREFIX}sil <isim>`\n"
                + ("↳ Kanalı siler" if lang_tr else "↳ Deletes a channel")
            ),
            "mod": (
                f"{t(gid, 'cat_mod')}\n\n"
                f"`{PREFIX}mute @kullanıcı [süre] [sebep]`\n`{PREFIX}unmute @kullanıcı`\n"
                f"`{PREFIX}kick @kullanıcı [sebep]`\n`{PREFIX}ban @kullanıcı [sebep]`\n`{PREFIX}unban <id>`\n"
                f"`{PREFIX}warn @kullanıcı [sebep]`\n`{PREFIX}warnings @kullanıcı`\n`{PREFIX}clear <adet>`"
            ),
            "verify": (
                f"{t(gid, 'cat_verify')}\n\n"
                f"`{PREFIX}verify-setup @rol`\n"
                + ("↳ Doğrulama panelini kurar. Butona basan kullanıcı belirtilen rolü alır."
                   if lang_tr else
                   "↳ Sets up the verification panel. Users who click the button get the specified role.")
            ),
            "ticket": (
                f"{t(gid, 'cat_ticket')}\n\n"
                f"`{PREFIX}ticket-setup`\n"
                + ("↳ Destek talebi panelini kurar. Kullanıcılar özel kanal açabilir."
                   if lang_tr else
                   "↳ Sets up the ticket panel. Users can open a private support channel.")
            ),
            "roles": (
                f"{t(gid, 'cat_roles')}\n\n"
                f"`{PREFIX}rol-olustur <isim> [#renkkodu]`\n`{PREFIX}rolmenu @rol1 @rol2 ...`\n"
                + ("↳ Kendi kendine rol seçim menüsü kurar." if lang_tr
                   else "↳ Sets up a self-assignable role menu.")
            ),
            "general": (
                f"{t(gid, 'cat_general')}\n\n"
                f"`{PREFIX}help`\n`{PREFIX}ping`\n`{PREFIX}sunucu`\n`{PREFIX}kullanici [@kullanıcı]`\n`{PREFIX}dil`"
            ),
        }[self.values[0]]

        embed = discord.Embed(title=t(gid, "help_title"), description=content, color=ACCENT_COLOR)
        embed.set_footer(text=f"{interaction.client.user.name} • {PREFIX}help")
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=120)
        self.add_item(HelpSelect(guild_id))


@bot.command(name="help")
async def help_command(ctx):
    gid = ctx.guild.id
    embed = discord.Embed(
        title=t(gid, "help_title"),
        description=t(gid, "help_desc"),
        color=ACCENT_COLOR
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"{bot.user.name} • {PREFIX}help")
    await ctx.send(embed=embed, view=HelpView(gid))


@bot.command()
async def ping(ctx):
    start = time.monotonic()
    msg = await ctx.send(t(ctx.guild.id, "ping_measuring"))
    elapsed = (time.monotonic() - start) * 1000
    embed = discord.Embed(
        title=t(ctx.guild.id, "ping_title"), color=ACCENT_COLOR,
        description=t(ctx.guild.id, "ping_desc", api=f"{bot.latency*1000:.0f}", msg=f"{elapsed:.0f}")
    )
    await msg.edit(content=None, embed=embed)


@bot.command(name="server")
async def server_info(ctx):
    guild = ctx.guild
    gid = guild.id
    embed = discord.Embed(title=f"📊 {guild.name}", color=ACCENT_COLOR)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name=t(gid, "server_owner"), value=guild.owner.mention if guild.owner else t(gid, "server_unknown"), inline=True)
    embed.add_field(name=t(gid, "server_members"), value=guild.member_count, inline=True)
    embed.add_field(name=t(gid, "server_channels"), value=len(guild.channels), inline=True)
    embed.add_field(name=t(gid, "server_roles"), value=len(guild.roles), inline=True)
    embed.add_field(name=t(gid, "server_created"), value=discord.utils.format_dt(guild.created_at, "D"), inline=True)
    await ctx.send(embed=embed)


@bot.command(name="kullanici")
async def user_info(ctx, member: discord.Member = None):
    member = member or ctx.author
    gid = ctx.guild.id
    embed = discord.Embed(title=f"👤 {member.display_name}", color=ACCENT_COLOR)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name=t(gid, "user_username"), value=str(member), inline=True)
    embed.add_field(name=t(gid, "user_id"), value=member.id, inline=True)
    embed.add_field(name=t(gid, "user_joined"), value=discord.utils.format_dt(member.joined_at, "D"), inline=True)
    embed.add_field(name=t(gid, "user_created"), value=discord.utils.format_dt(member.created_at, "D"), inline=True)
    top_role = member.top_role.mention if member.top_role.name != "@everyone" else t(gid, "user_no_role")
    embed.add_field(name=t(gid, "user_top_role"), value=top_role, inline=True)
    await ctx.send(embed=embed)


@bot.command(name="owner")
async def owner_info(ctx):
    owner_id = 1487413399653716048
    embed = discord.Embed(
        title="👑 Bot Owner",
        description=f"Bot owner: **<@{owner_id}>**\n\n**Discord ID:** `{owner_id}`",
        color=ACCENT_COLOR
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="Want this bot for free?", value="[Click here](https://discord.com/users/1487413399653716048)", inline=False)
    embed.set_footer(text=f"{bot.user.name} • hi lol")
    await ctx.send(embed=embed)


bot.run(TOKEN)
