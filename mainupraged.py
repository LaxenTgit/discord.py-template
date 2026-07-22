"ts code better than old"

import discord
from discord.ext import commands
from datetime import timedelta, datetime
import os
import re
import json
import time
import asyncio
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------------------------------------------------------------------------
# THEME / EMBED STYLING
# ---------------------------------------------------------------------------
ACCENT_COLOR = 0x8B5CF6
SUCCESS_COLOR = 0x57F287
DANGER_COLOR = 0xED4245
WARNING_COLOR = 0xFEE75C
INFO_COLOR = 0x5865F2
MUSIC_COLOR = 0xEB459E

DATA_FILE = "botdata.json"

YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


def base_embed(guild_id: int, title: str, description: str = None, color: int = ACCENT_COLOR) -> discord.Embed:
    """Builds a consistent, 'human' looking embed with timestamp + footer branding."""
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.utcnow())
    embed.set_footer(text=f"{bot.user.name if bot.user else 'Bot'} • {PREFIX}help",
                      icon_url=bot.user.display_avatar.url if bot.user else None)
    return embed


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

    "channel_created_text": {"tr": "Yeni bir metin kanalı açıldı ve kullanıma hazır.", "en": "A new text channel has been created and is ready to use."},
    "channel_created_voice": {"tr": "Yeni bir ses kanalı açıldı ve kullanıma hazır.", "en": "A new voice channel has been created and is ready to use."},
    "channel_invalid_type": {"tr": "Geçersiz kanal türü girdin.\nKullanım: `{p}kanal <text|voice> <isim>`",
                              "en": "Invalid channel type.\nUsage: `{p}kanal <text|voice> <name>`"},
    "channel_not_found": {"tr": "`{name}` adlı bir kanal bulamadım.", "en": "I couldn't find a channel named `{name}`."},
    "channel_deleted": {"tr": "`{name}` adlı kanal kalıcı olarak silindi.", "en": "Channel `{name}` has been permanently deleted."},

    "mute_invalid_duration": {"tr": "Süre formatı geçersiz. Örnek: `10m`, `2h`, `1d`",
                               "en": "Invalid duration format. Example: `10m`, `2h`, `1d`"},
    "mute_max_duration": {"tr": "Discord en fazla 28 günlük timeout izni veriyor, daha uzun bir süre veremiyorum.",
                           "en": "Discord only allows timeouts up to 28 days, I can't set anything longer."},
    "mute_title": {"tr": "🔇 Susturma Uygulandı", "en": "🔇 Timeout Applied"},
    "mute_desc": {"tr": "{member} sunucuda geçici olarak susturuldu.", "en": "{member} has been temporarily muted in this server."},
    "mute_field_duration": {"tr": "Süre", "en": "Duration"},
    "mute_field_mod": {"tr": "İşlemi Yapan", "en": "Moderator"},
    "mute_field_reason": {"tr": "Sebep", "en": "Reason"},
    "mute_dm": {"tr": "🔇 **{guild}** sunucusunda {duration} süreyle susturuldun.\nSebep: {reason}",
                "en": "🔇 You have been muted in **{guild}** for {duration}.\nReason: {reason}"},
    "unmute_not_muted": {"tr": "Bu üyenin zaten bir susturması bulunmuyor.", "en": "This member isn't currently muted."},
    "unmute_success": {"tr": "{member} kullanıcısının susturması kaldırıldı, tekrar mesaj gönderebilir.", "en": "{member}'s timeout has been removed, they can speak again."},

    "kick_title": {"tr": "👢 Üye Sunucudan Uzaklaştırıldı", "en": "👢 Member Removed"},
    "kick_desc": {"tr": "{member} sunucudan atıldı.", "en": "{member} has been kicked from the server."},
    "ban_title": {"tr": "🔨 Üye Yasaklandı", "en": "🔨 Member Banned"},
    "ban_desc": {"tr": "{member} sunucudan kalıcı olarak yasaklandı.", "en": "{member} has been permanently banned from the server."},
    "unban_success": {"tr": "`{id}` ID'li kullanıcının yasağı başarıyla kaldırıldı.", "en": "The ban for user ID `{id}` has been successfully lifted."},
    "unban_not_found": {"tr": "Bu ID'ye sahip yasaklı bir kullanıcı bulamadım.", "en": "I couldn't find a banned user with that ID."},

    "warn_title": {"tr": "⚠️ Uyarı Kaydedildi", "en": "⚠️ Warning Logged"},
    "warn_desc": {"tr": "{member} için yeni bir uyarı oluşturuldu. (Toplam: {count})", "en": "A new warning has been logged for {member}. (Total: {count})"},
    "warn_none": {"tr": "{member} için kayıtlı hiçbir uyarı yok, geçmişi temiz.", "en": "{member} has no warnings on record — clean history."},
    "warn_history_title": {"tr": "⚠️ {member} — Uyarı Geçmişi", "en": "⚠️ {member} — Warning History"},

    "clear_invalid_range": {"tr": "1 ile 100 arasında bir sayı girmelisin.", "en": "Please enter a number between 1 and 100."},
    "clear_success": {"tr": "{count} mesaj başarıyla temizlendi.", "en": "{count} messages have been cleared."},

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

    "verify_no_role_arg": {"tr": "Kullanım: `{p}verify-setup @rol`", "en": "Usage: `{p}verify-setup @role`"},
    "verify_setup_success": {"tr": "Doğrulama paneli başarıyla kuruldu.", "en": "Verification panel has been set up."},
    "verify_panel_title": {"tr": "✅ Sunucuya Hoş Geldin!", "en": "✅ Welcome to the Server!"},
    "verify_panel_desc": {"tr": "Sunucunun tüm kanallarına erişmek için aşağıdaki butona tıklayarak doğrulama yap.",
                           "en": "Click the button below to verify and unlock access to the server."},
    "verify_button_label": {"tr": "Doğrula", "en": "Verify"},
    "verify_already": {"tr": "Zaten doğrulanmışsın, tekrar işlem yapmana gerek yok.", "en": "You're already verified, no need to do this again."},
    "verify_success": {"tr": "Doğrulama başarılı! Artık sunucudaki tüm kanallara erişebilirsin.", "en": "Verification successful! You now have access to the server."},
    "verify_role_missing": {"tr": "Doğrulama rolü artık mevcut değil, lütfen bir yetkiliye bildir.",
                             "en": "The verification role no longer exists, please notify a staff member."},

    "ticket_setup_success": {"tr": "Destek talebi paneli kuruldu.", "en": "Ticket panel has been set up."},
    "ticket_panel_title": {"tr": "🎫 Destek Talebi Oluştur", "en": "🎫 Open a Support Ticket"},
    "ticket_panel_desc": {"tr": "Yardıma mı ihtiyacın var? Aşağıdaki butona tıklayarak özel bir destek kanalı aç, ekibimiz sana yardımcı olacak.",
                           "en": "Need help? Click the button below to open a private support channel — our team will assist you shortly."},
    "ticket_button_label": {"tr": "Talep Oluştur", "en": "Create Ticket"},
    "ticket_already_open": {"tr": "Zaten açık bir talebin var: {channel}", "en": "You already have an open ticket: {channel}"},
    "ticket_created": {"tr": "Talebin oluşturuldu: {channel}", "en": "Your ticket has been created: {channel}"},
    "ticket_welcome_title": {"tr": "🎫 Destek Talebi", "en": "🎫 Support Ticket"},
    "ticket_welcome_desc": {"tr": "{member}, talebini açtın. Bir yetkili en kısa sürede seninle ilgilenecek.\nKapatmak için aşağıdaki butona tıklayabilirsin.",
                             "en": "{member}, your ticket has been opened. Staff will assist you shortly.\nClick the button below to close it."},
    "ticket_close_label": {"tr": "Talebi Kapat", "en": "Close Ticket"},
    "ticket_closing": {"tr": "Bu talep 5 saniye içinde kapanacak...", "en": "This ticket will close in 5 seconds..."},

    "role_create_success": {"tr": "`{name}` rolü başarıyla oluşturuldu.", "en": "Role `{name}` has been created successfully."},
    "role_create_usage": {"tr": "Kullanım: `{p}rol-olustur <isim> [#renkkodu]`", "en": "Usage: `{p}rol-olustur <name> [#colorcode]`"},
    "role_create_bad_color": {"tr": "Geçersiz renk kodu girdin. Örnek: `#8B5CF6`", "en": "Invalid color code. Example: `#8B5CF6`"},

    "rolemenu_usage": {"tr": "Kullanım: `{p}rolmenu @rol1 @rol2 ...` (en az 1, en fazla 25 rol)",
                        "en": "Usage: `{p}rolmenu @role1 @role2 ...` (1 to 25 roles)"},
    "rolemenu_setup_success": {"tr": "Rol seçim paneli kuruldu.", "en": "Role selection panel has been set up."},
    "rolemenu_panel_title": {"tr": "🎭 Rol Seçimi", "en": "🎭 Role Selection"},
    "rolemenu_panel_desc": {"tr": "Aşağıdaki menüden istediğin rolleri seç. Tekrar seçerek kaldırabilirsin.",
                             "en": "Pick your roles from the menu below. Select again to remove them."},
    "rolemenu_placeholder": {"tr": "Rollerini seç...", "en": "Select your roles..."},
    "rolemenu_updated": {"tr": "Rollerin güncellendi.", "en": "Your roles have been updated."},

    "err_missing_perms": {"tr": "Bu komutu kullanmak için yeterli yetkin yok.", "en": "You don't have permission to use this command."},
    "err_bot_missing_perms": {"tr": "Bu işlemi yapabilmem için gereken yetkiye sahip değilim.", "en": "I lack the required permission to do this."},
    "err_missing_arg": {"tr": "Eksik bir argüman var. `{p}help` ile kullanımı kontrol edebilirsin.",
                         "en": "A required argument is missing. Check `{p}help` for usage."},
    "err_bad_arg": {"tr": "Girdiğin argüman geçersiz görünüyor.", "en": "The argument you provided looks invalid."},
    "err_member_not_found": {"tr": "Böyle bir üye bulamadım.", "en": "I couldn't find that member."},
    "err_cooldown": {"tr": "Bu komut şu an bekleme süresinde, {s:.1f} saniye sonra tekrar dene.",
                      "en": "This command is on cooldown, try again in {s:.1f}s."},
    "err_unexpected": {"tr": "Beklenmedik bir hata oluştu, tekrar denemeni öneririm.", "en": "An unexpected error occurred, please try again."},

    "help_title": {"tr": "⚙️ Komut Menüsü", "en": "⚙️ Command Menu"},
    "help_desc": {"tr": "Aşağıdaki menüden bir kategori seç ve o kategoriye ait komutları keşfet.",
                  "en": "Pick a category from the menu below to explore its commands."},
    "help_placeholder": {"tr": "Bir kategori seç...", "en": "Choose a category..."},
    "cat_channels": {"tr": "📁 Kanal Yönetimi", "en": "📁 Channel Management"},
    "cat_mod": {"tr": "🛡️ Moderasyon", "en": "🛡️ Moderation"},
    "cat_verify": {"tr": "✅ Doğrulama", "en": "✅ Verification"},
    "cat_ticket": {"tr": "🎫 Destek Talebi", "en": "🎫 Tickets"},
    "cat_roles": {"tr": "🎭 Rol Sistemi", "en": "🎭 Role System"},
    "cat_general": {"tr": "🔧 Genel", "en": "🔧 General"},
    "cat_music": {"tr": "🎵 Müzik", "en": "🎵 Music"},

    "music_not_in_voice": {"tr": "Bu komutu kullanabilmek için önce bir ses kanalına girmen gerekiyor.", "en": "You need to join a voice channel first to use this."},
    "music_joined": {"tr": "Ses kanalına katıldım, hazırım.", "en": "Joined the voice channel, ready to go."},
    "music_playing": {"tr": "🎵 Şimdi çalıyor: **{title}**", "en": "🎵 Now playing: **{title}**"},
    "music_error": {"tr": "Bir şeyler ters gitti: {error}", "en": "Something went wrong: {error}"},
    "music_left": {"tr": "Ses kanalından ayrıldım, kuyruk temizlendi.", "en": "Left the voice channel, queue cleared."},
    "music_not_in_channel": {"tr": "Zaten herhangi bir ses kanalında değilim.", "en": "I'm not currently in a voice channel."},
    "music_added": {"tr": "Kuyruğa eklendi: **{title}** (sıra #{pos})", "en": "Added to queue: **{title}** (position #{pos})"},
    "music_queue_empty": {"tr": "Kuyrukta hiçbir şarkı yok.", "en": "The queue is currently empty."},
    "music_queue_title": {"tr": "🎵 Şarkı Kuyruğu", "en": "🎵 Song Queue"},
    "music_now_playing": {"tr": "Şu An Çalıyor", "en": "Now Playing"},
    "music_up_next": {"tr": "Sırada", "en": "Up Next"},
    "music_requested_by": {"tr": "İsteyen", "en": "Requested by"},
    "music_position": {"tr": "Kuyruk Sırası", "en": "Queue Position"},
    "music_skipped": {"tr": "Şarkı atlandı, sıradaki geliyor.", "en": "Song skipped, moving to the next one."},
    "music_no_next": {"tr": "Sırada başka bir şarkı yok.", "en": "There's no next song in the queue."},
    "music_paused": {"tr": "⏸️ Şarkı duraklatıldı.", "en": "⏸️ Playback paused."},
    "music_resumed": {"tr": "▶️ Şarkı kaldığı yerden devam ediyor.", "en": "▶️ Playback resumed."},
    "music_not_playing": {"tr": "Şu anda çalan bir şarkı yok.", "en": "Nothing is currently playing."},
    "music_stopped": {"tr": "⏹️ Çalma durduruldu ve kuyruk tamamen temizlendi.", "en": "⏹️ Playback stopped and the queue has been cleared."},
    "music_volume_set": {"tr": "🔊 Ses seviyesi %{volume} olarak ayarlandı.", "en": "🔊 Volume set to {volume}%."},
    "music_volume_invalid": {"tr": "Ses seviyesi 0 ile 200 arasında olmalı.", "en": "Volume must be between 0 and 200."},
    "music_shuffled": {"tr": "🔀 Kuyruk karıştırıldı.", "en": "🔀 Queue shuffled."},
    "music_loop_on": {"tr": "🔁 Tekrar modu açıldı, mevcut şarkı sürekli çalacak.", "en": "🔁 Loop mode enabled, the current song will repeat."},
    "music_loop_off": {"tr": "➡️ Tekrar modu kapatıldı.", "en": "➡️ Loop mode disabled."},
    "music_removed": {"tr": "Kuyruktan `#{pos}` numaralı şarkı çıkarıldı: **{title}**", "en": "Removed song `#{pos}` from queue: **{title}**"},
    "music_remove_invalid": {"tr": "Geçersiz sıra numarası girdin.", "en": "Invalid queue position provided."},
    "music_nothing_queued": {"tr": "Kuyrukta ve çalmakta olan hiçbir şey yok.", "en": "Nothing is playing and the queue is empty."},
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


def format_duration(seconds: int) -> str:
    if not seconds:
        return "??:??"
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


warnings_db = {}
open_tickets = {}


# ---------------------------------------------------------------------------
# MUSIC SYSTEM
# ---------------------------------------------------------------------------
class Track:
    __slots__ = ("url", "title", "webpage_url", "duration", "thumbnail", "requester")

    def __init__(self, url, title, webpage_url, duration, thumbnail, requester):
        self.url = url
        self.title = title
        self.webpage_url = webpage_url
        self.duration = duration
        self.thumbnail = thumbnail
        self.requester = requester


class GuildMusicState:
    """Per-guild music state: queue, loop flag, volume, now playing."""

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.queue: list[Track] = []
        self.now_playing: Track | None = None
        self.loop: bool = False
        self.volume: float = 1.0
        self.text_channel: discord.abc.Messageable | None = None
        self.skip_flag: bool = False

    def next_track(self) -> Track | None:
        if self.loop and self.now_playing:
            return self.now_playing
        if not self.queue:
            return None
        return self.queue.pop(0)


music_states: dict[int, GuildMusicState] = {}


def get_music_state(guild_id: int) -> GuildMusicState:
    return music_states.setdefault(guild_id, GuildMusicState(guild_id))


async def extract_track(query: str, requester: discord.Member) -> Track:
    loop = asyncio.get_event_loop()

    def _extract():
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}" if not query.startswith("http") else query, download=False)
            entries = info.get("entries")
            return entries[0] if entries else info

    data = await loop.run_in_executor(None, _extract)
    return Track(
        url=data["url"],
        title=data.get("title", "Bilinmeyen Şarkı"),
        webpage_url=data.get("webpage_url", ""),
        duration=data.get("duration", 0),
        thumbnail=data.get("thumbnail"),
        requester=requester,
    )


def play_next(guild: discord.Guild):
    """Callback chain: called when a track finishes, plays the next one."""
    state = get_music_state(guild.id)
    voice_client = guild.voice_client

    if voice_client is None:
        return

    track = state.next_track()
    if track is None:
        state.now_playing = None
        return

    state.now_playing = track
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track.url, **FFMPEG_OPTS), volume=state.volume)

    def _after(error):
        if error:
            print(f"[music] playback error: {error}")
        play_next(guild)

    voice_client.play(source, after=_after)

    if state.text_channel:
        gid = guild.id
        embed = base_embed(gid, f"🎵 {t(gid, 'music_now_playing')}", color=MUSIC_COLOR)
        embed.description = f"**[{track.title}]({track.webpage_url})**"
        embed.add_field(name="⏱️", value=format_duration(track.duration), inline=True)
        embed.add_field(name=t(gid, "music_requested_by"), value=track.requester.mention, inline=True)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)
        asyncio.run_coroutine_threadsafe(state.text_channel.send(embed=embed), bot.loop)


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
        embed = base_embed(gid, "❌ Yetki Yetersiz" if get_lang(gid) == "tr" else "❌ Missing Permissions",
                            t(gid, "err_missing_perms"), DANGER_COLOR)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = base_embed(gid, "❌ Bot Yetkisi Eksik" if get_lang(gid) == "tr" else "❌ Bot Missing Permissions",
                            t(gid, "err_bot_missing_perms"), DANGER_COLOR)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = base_embed(gid, "❌ Eksik Argüman" if get_lang(gid) == "tr" else "❌ Missing Argument",
                            t(gid, "err_missing_arg"), WARNING_COLOR)
    elif isinstance(error, commands.BadArgument):
        embed = base_embed(gid, "❌ Geçersiz Argüman" if get_lang(gid) == "tr" else "❌ Invalid Argument",
                            t(gid, "err_bad_arg"), WARNING_COLOR)
    elif isinstance(error, commands.MemberNotFound):
        embed = base_embed(gid, "❌ Üye Bulunamadı" if get_lang(gid) == "tr" else "❌ Member Not Found",
                            t(gid, "err_member_not_found"), WARNING_COLOR)
    elif isinstance(error, commands.CommandOnCooldown):
        embed = base_embed(gid, "⏳ Bekleme Süresi" if get_lang(gid) == "tr" else "⏳ Cooldown",
                            t(gid, "err_cooldown", s=error.retry_after), WARNING_COLOR)
    else:
        embed = base_embed(gid, "❌ Hata" if get_lang(gid) == "tr" else "❌ Error",
                            t(gid, "err_unexpected"), DANGER_COLOR)
        await ctx.send(embed=embed)
        raise error

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def kanal(ctx, tur: str, *, isim: str):
    tur = tur.lower()
    gid = ctx.guild.id
    if tur in ("text", "metin"):
        channel = await ctx.guild.create_text_channel(name=isim)
        embed = base_embed(gid, "📁 Kanal Oluşturuldu" if get_lang(gid) == "tr" else "📁 Channel Created",
                            t(gid, "channel_created_text"), SUCCESS_COLOR)
        embed.add_field(name="Kanal" if get_lang(gid) == "tr" else "Channel", value=channel.mention)
        await ctx.send(embed=embed)
    elif tur in ("voice", "ses"):
        channel = await ctx.guild.create_voice_channel(name=isim)
        embed = base_embed(gid, "📁 Kanal Oluşturuldu" if get_lang(gid) == "tr" else "📁 Channel Created",
                            t(gid, "channel_created_voice"), SUCCESS_COLOR)
        embed.add_field(name="Kanal" if get_lang(gid) == "tr" else "Channel", value=f"`{channel.name}`")
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=base_embed(gid, "❌ Hatalı Kullanım", t(gid, "channel_invalid_type"), DANGER_COLOR))


@bot.command()
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def sil(ctx, *, isim: str):
    gid = ctx.guild.id
    channel = discord.utils.get(ctx.guild.channels, name=isim)
    if channel is None:
        await ctx.send(embed=base_embed(gid, "❌ Bulunamadı", t(gid, "channel_not_found", name=isim), DANGER_COLOR))
        return
    await channel.delete()
    await ctx.send(embed=base_embed(gid, "🗑️ Kanal Silindi" if get_lang(gid) == "tr" else "🗑️ Channel Deleted",
                                     t(gid, "channel_deleted", name=isim), SUCCESS_COLOR))


@bot.command()
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: str = "10m", *, sebep: str = None):
    gid = ctx.guild.id
    reason = sebep or ("Sebep belirtilmedi" if get_lang(gid) == "tr" else "No reason provided")
    delta = parse_duration(duration)
    if delta is None:
        await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "mute_invalid_duration"), DANGER_COLOR))
        return
    if delta > timedelta(days=28):
        await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "mute_max_duration"), DANGER_COLOR))
        return

    await member.timeout(delta, reason=f"{ctx.author}: {reason}")

    embed = base_embed(gid, t(gid, "mute_title"), t(gid, "mute_desc", member=member.mention), WARNING_COLOR)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name=t(gid, "mute_field_duration"), value=duration, inline=True)
    embed.add_field(name=t(gid, "mute_field_mod"), value=ctx.author.mention, inline=True)
    embed.add_field(name=t(gid, "mute_field_reason"), value=reason, inline=False)
    await ctx.send(embed=embed)

    try:
        await member.send(t(gid, "mute_dm", guild=ctx.guild.name, duration=duration, reason=reason))
    except discord.Forbidden:
        pass


@bot.command()
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    gid = ctx.guild.id
    if member.timed_out_until is None:
        await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "unmute_not_muted"), DANGER_COLOR))
        return
    await member.timeout(None, reason=f"Unmuted by {ctx.author}")
    embed = base_embed(gid, "🔊 Susturma Kaldırıldı" if get_lang(gid) == "tr" else "🔊 Timeout Removed",
                        t(gid, "unmute_success", member=member.mention), SUCCESS_COLOR)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(kick_members=True)
@commands.bot_has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep: str = None):
    gid = ctx.guild.id
    reason = sebep or ("Sebep belirtilmedi" if get_lang(gid) == "tr" else "No reason provided")
    avatar_url = member.display_avatar.url
    await member.kick(reason=f"{ctx.author}: {reason}")
    embed = base_embed(gid, t(gid, "kick_title"), t(gid, "kick_desc", member=member.mention), DANGER_COLOR)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name=t(gid, "mute_field_mod"), value=ctx.author.mention, inline=True)
    embed.add_field(name=t(gid, "mute_field_reason"), value=reason, inline=True)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep: str = None):
    gid = ctx.guild.id
    reason = sebep or ("Sebep belirtilmedi" if get_lang(gid) == "tr" else "No reason provided")
    avatar_url = member.display_avatar.url
    await member.ban(reason=f"{ctx.author}: {reason}")
    embed = base_embed(gid, t(gid, "ban_title"), t(gid, "ban_desc", member=member.mention), DANGER_COLOR)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name=t(gid, "mute_field_mod"), value=ctx.author.mention, inline=True)
    embed.add_field(name=t(gid, "mute_field_reason"), value=reason, inline=True)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    gid = ctx.guild.id
    user = discord.Object(id=user_id)
    try:
        await ctx.guild.unban(user)
        await ctx.send(embed=base_embed(gid, "✅ Yasak Kaldırıldı" if get_lang(gid) == "tr" else "✅ Ban Removed",
                                         t(gid, "unban_success", id=user_id), SUCCESS_COLOR))
    except discord.NotFound:
        await ctx.send(embed=base_embed(gid, "❌ Bulunamadı", t(gid, "unban_not_found"), DANGER_COLOR))


@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, sebep: str = None):
    gid = ctx.guild.id
    reason = sebep or ("Sebep belirtilmedi" if get_lang(gid) == "tr" else "No reason provided")
    guild_warns = warnings_db.setdefault(ctx.guild.id, {})
    user_warns = guild_warns.setdefault(member.id, [])
    user_warns.append(reason)

    embed = base_embed(gid, t(gid, "warn_title"), t(gid, "warn_desc", member=member.mention, count=len(user_warns)), WARNING_COLOR)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name=t(gid, "mute_field_reason"), value=reason, inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def warnings(ctx, member: discord.Member):
    gid = ctx.guild.id
    user_warns = warnings_db.get(ctx.guild.id, {}).get(member.id, [])
    if not user_warns:
        await ctx.send(embed=base_embed(gid, "✅ Temiz Sicil" if get_lang(gid) == "tr" else "✅ Clean Record",
                                         t(gid, "warn_none", member=member.mention), SUCCESS_COLOR))
        return
    embed = base_embed(
        gid,
        t(gid, "warn_history_title", member=member.display_name),
        "\n".join(f"`{i+1}.` {r}" for i, r in enumerate(user_warns)),
        WARNING_COLOR
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def clear(ctx, adet: int):
    gid = ctx.guild.id
    if adet < 1 or adet > 100:
        await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "clear_invalid_range"), DANGER_COLOR))
        return
    deleted = await ctx.channel.purge(limit=adet + 1)
    embed = base_embed(gid, "🧹 Temizlik Tamamlandı" if get_lang(gid) == "tr" else "🧹 Cleanup Complete",
                        t(gid, "clear_success", count=len(deleted) - 1), SUCCESS_COLOR)
    msg = await ctx.send(embed=embed)
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
    gid = ctx.guild.id
    if role is None:
        await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "verify_no_role_arg"), DANGER_COLOR))
        return

    set_guild_data(gid, "verify_role_id", role.id)

    embed = base_embed(gid, t(gid, "verify_panel_title"), t(gid, "verify_panel_desc"), SUCCESS_COLOR)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    view = VerifyView(role.id)
    await ctx.send(embed=embed, view=view)
    bot.add_view(view)


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = interaction.guild.id
        embed = base_embed(gid, "🔒 Talep Kapanıyor" if get_lang(gid) == "tr" else "🔒 Closing Ticket",
                            t(gid, "ticket_closing"), WARNING_COLOR)
        await interaction.response.send_message(embed=embed)

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
                    embed=base_embed(gid, "❌ Zaten Var", t(gid, "ticket_already_open", channel=existing_channel.mention), WARNING_COLOR),
                    ephemeral=True
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

        embed = base_embed(gid, t(gid, "ticket_welcome_title"), t(gid, "ticket_welcome_desc", member=user.mention), ACCENT_COLOR)
        embed.set_thumbnail(url=user.display_avatar.url)
        await channel.send(embed=embed, view=TicketCloseView())
        await interaction.response.send_message(
            embed=base_embed(gid, "✅ Talep Oluşturuldu" if get_lang(gid) == "tr" else "✅ Ticket Created",
                              t(gid, "ticket_created", channel=channel.mention), SUCCESS_COLOR),
            ephemeral=True
        )


@bot.command(name="ticket-setup")
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_channels=True)
async def ticket_setup(ctx):
    gid = ctx.guild.id
    embed = base_embed(gid, t(gid, "ticket_panel_title"), t(gid, "ticket_panel_desc"), ACCENT_COLOR)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=TicketPanelView())


@bot.command(name="rol-olustur")
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def rol_olustur(ctx, isim: str, renk: str = None):
    gid = ctx.guild.id
    color = discord.Color(ACCENT_COLOR)
    if renk:
        try:
            color = discord.Color(int(renk.lstrip("#"), 16))
        except ValueError:
            await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "role_create_bad_color"), DANGER_COLOR))
            return

    role = await ctx.guild.create_role(name=isim, color=color, reason=f"{ctx.author} tarafından oluşturuldu")
    embed = base_embed(gid, "🎭 Rol Oluşturuldu" if get_lang(gid) == "tr" else "🎭 Role Created",
                        t(gid, "role_create_success", name=role.name), SUCCESS_COLOR)
    await ctx.send(embed=embed)


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
    gid = ctx.guild.id
    if not roles or len(roles) > 25:
        await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "rolemenu_usage"), DANGER_COLOR))
        return

    role_ids = [r.id for r in roles]
    role_names = {r.id: r.name for r in roles}
    set_guild_data(gid, "selfroles", role_ids)

    select = RoleMenuSelect(role_ids, role_names)
    select.placeholder = t(gid, "rolemenu_placeholder")

    view = discord.ui.View(timeout=None)
    view.add_item(select)

    embed = base_embed(gid, t(gid, "rolemenu_panel_title"), t(gid, "rolemenu_panel_desc"), ACCENT_COLOR)
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
            discord.SelectOption(label=t(guild_id, "cat_music"), value="music", emoji="🎵"),
            discord.SelectOption(label=t(guild_id, "cat_general"), value="general", emoji="🔧"),
        ]
        super().__init__(placeholder=t(guild_id, "help_placeholder"), options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        gid = interaction.guild.id
        lang_tr = get_lang(gid) == "tr"
        content = {
            "channels": (
                f"`{PREFIX}kanal <text|voice> <isim>`\n"
                + ("↳ Kanal oluşturur\n\n" if lang_tr else "↳ Creates a channel\n\n")
                + f"`{PREFIX}sil <isim>`\n"
                + ("↳ Kanalı siler" if lang_tr else "↳ Deletes a channel")
            ),
            "mod": (
                f"`{PREFIX}mute @kullanıcı [süre] [sebep]`\n`{PREFIX}unmute @kullanıcı`\n"
                f"`{PREFIX}kick @kullanıcı [sebep]`\n`{PREFIX}ban @kullanıcı [sebep]`\n`{PREFIX}unban <id>`\n"
                f"`{PREFIX}warn @kullanıcı [sebep]`\n`{PREFIX}warnings @kullanıcı`\n`{PREFIX}clear <adet>`"
            ),
            "verify": (
                f"`{PREFIX}verify-setup @rol`\n"
                + ("↳ Doğrulama panelini kurar. Butona basan kullanıcı belirtilen rolü alır."
                   if lang_tr else
                   "↳ Sets up the verification panel. Users who click the button get the specified role.")
            ),
            "ticket": (
                f"`{PREFIX}ticket-setup`\n"
                + ("↳ Destek talebi panelini kurar. Kullanıcılar özel kanal açabilir."
                   if lang_tr else
                   "↳ Sets up the ticket panel. Users can open a private support channel.")
            ),
            "roles": (
                f"`{PREFIX}rol-olustur <isim> [#renkkodu]`\n`{PREFIX}rolmenu @rol1 @rol2 ...`\n"
                + ("↳ Kendi kendine rol seçim menüsü kurar." if lang_tr
                   else "↳ Sets up a self-assignable role menu.")
            ),
            "music": (
                f"`{PREFIX}join` — " + ("Ses kanalına katılır" if lang_tr else "Joins your voice channel") + "\n"
                f"`{PREFIX}play <isim/link>` — " + ("Şarkı çalar veya kuyruğa ekler" if lang_tr else "Plays or queues a song") + "\n"
                f"`{PREFIX}skip` — " + ("Şarkıyı atlar" if lang_tr else "Skips the current song") + "\n"
                f"`{PREFIX}pause` / `{PREFIX}resume` — " + ("Duraklat / devam ettir" if lang_tr else "Pause / resume playback") + "\n"
                f"`{PREFIX}stop` — " + ("Çalmayı durdurur, kuyruğu temizler" if lang_tr else "Stops playback, clears queue") + "\n"
                f"`{PREFIX}queue` — " + ("Kuyruğu gösterir" if lang_tr else "Shows the queue") + "\n"
                f"`{PREFIX}nowplaying` — " + ("Çalan şarkıyı gösterir" if lang_tr else "Shows the current song") + "\n"
                f"`{PREFIX}remove <sıra>` — " + ("Kuyruktan şarkı çıkarır" if lang_tr else "Removes a song from queue") + "\n"
                f"`{PREFIX}shuffle` — " + ("Kuyruğu karıştırır" if lang_tr else "Shuffles the queue") + "\n"
                f"`{PREFIX}loop` — " + ("Tekrar modunu açar/kapatır" if lang_tr else "Toggles loop mode") + "\n"
                f"`{PREFIX}volume <0-200>` — " + ("Ses seviyesini ayarlar" if lang_tr else "Sets the volume") + "\n"
                f"`{PREFIX}leave` — " + ("Ses kanalından ayrılır" if lang_tr else "Leaves the voice channel")
            ),
            "general": (
                f"`{PREFIX}help`\n`{PREFIX}ping`\n`{PREFIX}sunucu`\n`{PREFIX}kullanici [@kullanıcı]`\n`{PREFIX}dil`"
            ),
        }[self.values[0]]

        titles = {
            "channels": t(gid, "cat_channels"), "mod": t(gid, "cat_mod"), "verify": t(gid, "cat_verify"),
            "ticket": t(gid, "cat_ticket"), "roles": t(gid, "cat_roles"), "music": t(gid, "cat_music"),
            "general": t(gid, "cat_general"),
        }

        embed = base_embed(gid, titles[self.values[0]], content, ACCENT_COLOR)
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=120)
        self.add_item(HelpSelect(guild_id))


@bot.command(name="help")
async def help_command(ctx):
    gid = ctx.guild.id
    embed = base_embed(gid, t(gid, "help_title"), t(gid, "help_desc"), ACCENT_COLOR)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await ctx.send(embed=embed, view=HelpView(gid))


@bot.command()
async def ping(ctx):
    gid = ctx.guild.id
    start = time.monotonic()
    msg = await ctx.send(embed=base_embed(gid, t(gid, "ping_title"), t(gid, "ping_measuring"), INFO_COLOR))
    elapsed = (time.monotonic() - start) * 1000
    embed = base_embed(gid, t(gid, "ping_title"),
                        t(gid, "ping_desc", api=f"{bot.latency*1000:.0f}", msg=f"{elapsed:.0f}"), INFO_COLOR)
    await msg.edit(embed=embed)


@bot.command(name="sunucu")
async def server_info(ctx):
    guild = ctx.guild
    gid = guild.id
    embed = base_embed(gid, f"📊 {guild.name}", color=ACCENT_COLOR)
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
    embed = base_embed(gid, f"👤 {member.display_name}", color=ACCENT_COLOR)
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
    embed = base_embed(ctx.guild.id, "👑 Bot Owner",
                        f"Bot owner: **<@{owner_id}>**\n\n**Discord ID:** `{owner_id}`", ACCENT_COLOR)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="Want this bot for free?", value="[Click here](https://github.com/LaxenTgit/discord-bot-template)", inline=False)
    await ctx.send(embed=embed)


# ---------------------------------------------------------------------------
# MUSIC COMMANDS
# ---------------------------------------------------------------------------
@bot.command()
async def join(ctx):
    gid = ctx.guild.id
    if ctx.author.voice is None:
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_not_in_voice"), DANGER_COLOR))
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)
    state = get_music_state(gid)
    state.text_channel = ctx.channel
    await ctx.send(embed=base_embed(gid, "🔊 Bağlandım" if get_lang(gid) == "tr" else "🔊 Connected",
                                     t(gid, "music_joined"), MUSIC_COLOR))


@bot.command()
async def play(ctx, *, query):
    gid = ctx.guild.id
    if ctx.voice_client is None:
        if ctx.author.voice is None:
            return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_not_in_voice"), DANGER_COLOR))
        await ctx.author.voice.channel.connect()

    state = get_music_state(gid)
    state.text_channel = ctx.channel

    try:
        track = await extract_track(query, ctx.author)
    except Exception as e:
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_error", error=str(e)), DANGER_COLOR))

    voice_client = ctx.voice_client

    if voice_client.is_playing() or voice_client.is_paused() or state.now_playing:
        state.queue.append(track)
        embed = base_embed(gid, "➕ Kuyruğa Eklendi" if get_lang(gid) == "tr" else "➕ Added to Queue",
                            t(gid, "music_added", title=track.title, pos=len(state.queue)), MUSIC_COLOR)
        embed.add_field(name="⏱️", value=format_duration(track.duration), inline=True)
        embed.add_field(name=t(gid, "music_requested_by"), value=track.requester.mention, inline=True)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)
        await ctx.send(embed=embed)
    else:
        state.now_playing = track
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track.url, **FFMPEG_OPTS), volume=state.volume)

        def _after(error):
            if error:
                print(f"[music] playback error: {error}")
            play_next(ctx.guild)

        voice_client.play(source, after=_after)

        embed = base_embed(gid, f"🎵 {t(gid, 'music_now_playing')}", color=MUSIC_COLOR)
        embed.description = f"**[{track.title}]({track.webpage_url})**"
        embed.add_field(name="⏱️", value=format_duration(track.duration), inline=True)
        embed.add_field(name=t(gid, "music_requested_by"), value=track.requester.mention, inline=True)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)
        await ctx.send(embed=embed)


@bot.command()
async def skip(ctx):
    gid = ctx.guild.id
    if ctx.voice_client is None or not (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_not_playing"), DANGER_COLOR))
    ctx.voice_client.stop()  # triggers the `after` callback -> play_next
    await ctx.send(embed=base_embed(gid, "⏭️ Atlandı" if get_lang(gid) == "tr" else "⏭️ Skipped",
                                     t(gid, "music_skipped"), MUSIC_COLOR))


@bot.command()
async def pause(ctx):
    gid = ctx.guild.id
    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_not_playing"), DANGER_COLOR))
    ctx.voice_client.pause()
    await ctx.send(embed=base_embed(gid, "⏸️ Duraklatıldı" if get_lang(gid) == "tr" else "⏸️ Paused",
                                     t(gid, "music_paused"), MUSIC_COLOR))


@bot.command()
async def resume(ctx):
    gid = ctx.guild.id
    if ctx.voice_client is None or not ctx.voice_client.is_paused():
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_not_playing"), DANGER_COLOR))
    ctx.voice_client.resume()
    await ctx.send(embed=base_embed(gid, "▶️ Devam Ediyor" if get_lang(gid) == "tr" else "▶️ Resumed",
                                     t(gid, "music_resumed"), MUSIC_COLOR))


@bot.command()
async def stop(ctx):
    gid = ctx.guild.id
    state = get_music_state(gid)
    state.queue.clear()
    state.now_playing = None
    state.loop = False
    if ctx.voice_client:
        ctx.voice_client.stop()
    await ctx.send(embed=base_embed(gid, "⏹️ Durduruldu" if get_lang(gid) == "tr" else "⏹️ Stopped",
                                     t(gid, "music_stopped"), MUSIC_COLOR))


@bot.command()
async def queue(ctx):
    gid = ctx.guild.id
    state = get_music_state(gid)
    if not state.now_playing and not state.queue:
        return await ctx.send(embed=base_embed(gid, "❌ Boş" if get_lang(gid) == "tr" else "❌ Empty",
                                                 t(gid, "music_nothing_queued"), WARNING_COLOR))

    embed = base_embed(gid, t(gid, "music_queue_title"), color=MUSIC_COLOR)
    if state.now_playing:
        embed.add_field(
            name=f"▶️ {t(gid, 'music_now_playing')}",
            value=f"**{state.now_playing.title}** — {format_duration(state.now_playing.duration)} ({state.now_playing.requester.mention})",
            inline=False
        )
    if state.queue:
        lines = [
            f"`{i+1}.` **{track.title}** — {format_duration(track.duration)} ({track.requester.mention})"
            for i, track in enumerate(state.queue[:10])
        ]
        embed.add_field(name=t(gid, "music_up_next"), value="\n".join(lines), inline=False)
        if len(state.queue) > 10:
            embed.set_footer(text=f"+{len(state.queue) - 10} " + ("daha fazla şarkı..." if get_lang(gid) == "tr" else "more songs..."))
    await ctx.send(embed=embed)


@bot.command(aliases=["np"])
async def nowplaying(ctx):
    gid = ctx.guild.id
    state = get_music_state(gid)
    if not state.now_playing:
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_not_playing"), DANGER_COLOR))
    track = state.now_playing
    embed = base_embed(gid, f"🎵 {t(gid, 'music_now_playing')}", color=MUSIC_COLOR)
    embed.description = f"**[{track.title}]({track.webpage_url})**"
    embed.add_field(name="⏱️", value=format_duration(track.duration), inline=True)
    embed.add_field(name=t(gid, "music_requested_by"), value=track.requester.mention, inline=True)
    embed.add_field(name="🔁", value=("Açık" if state.loop else "Kapalı") if get_lang(gid) == "tr" else ("On" if state.loop else "Off"), inline=True)
    if track.thumbnail:
        embed.set_thumbnail(url=track.thumbnail)
    await ctx.send(embed=embed)


@bot.command()
async def remove(ctx, pos: int):
    gid = ctx.guild.id
    state = get_music_state(gid)
    if pos < 1 or pos > len(state.queue):
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_remove_invalid"), DANGER_COLOR))
    track = state.queue.pop(pos - 1)
    await ctx.send(embed=base_embed(gid, "🗑️ Kaldırıldı" if get_lang(gid) == "tr" else "🗑️ Removed",
                                     t(gid, "music_removed", pos=pos, title=track.title), MUSIC_COLOR))


@bot.command()
async def shuffle(ctx):
    gid = ctx.guild.id
    state = get_music_state(gid)
    if not state.queue:
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_queue_empty"), DANGER_COLOR))
    import random
    random.shuffle(state.queue)
    await ctx.send(embed=base_embed(gid, "🔀 Karıştırıldı" if get_lang(gid) == "tr" else "🔀 Shuffled",
                                     t(gid, "music_shuffled"), MUSIC_COLOR))


@bot.command()
async def loop(ctx):
    gid = ctx.guild.id
    state = get_music_state(gid)
    state.loop = not state.loop
    key = "music_loop_on" if state.loop else "music_loop_off"
    await ctx.send(embed=base_embed(gid, "🔁 Tekrar Modu" if get_lang(gid) == "tr" else "🔁 Loop Mode",
                                     t(gid, key), MUSIC_COLOR))


@bot.command()
async def volume(ctx, level: int):
    gid = ctx.guild.id
    if level < 0 or level > 200:
        return await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_volume_invalid"), DANGER_COLOR))
    state = get_music_state(gid)
    state.volume = level / 100
    if ctx.voice_client and ctx.voice_client.source:
        ctx.voice_client.source.volume = state.volume
    await ctx.send(embed=base_embed(gid, "🔊 Ses Ayarlandı" if get_lang(gid) == "tr" else "🔊 Volume Set",
                                     t(gid, "music_volume_set", volume=level), MUSIC_COLOR))


@bot.command()
async def leave(ctx):
    gid = ctx.guild.id
    if ctx.voice_client:
        state = get_music_state(gid)
        state.queue.clear()
        state.now_playing = None
        state.loop = False
        await ctx.voice_client.disconnect()
        await ctx.send(embed=base_embed(gid, "👋 Ayrıldım" if get_lang(gid) == "tr" else "👋 Left",
                                         t(gid, "music_left"), MUSIC_COLOR))
    else:
        await ctx.send(embed=base_embed(gid, "❌ Hata", t(gid, "music_not_in_channel"), DANGER_COLOR))


bot.run(TOKEN)
