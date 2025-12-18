import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

invite_cache = {}
invite_counts = {}

# Get token from environment variable (SECURE)
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set. Please set it before running the bot.")

PREFIX = "!"

LOGS_CHANNEL_ID = 1449299029103087697
SOURCE_CHANNEL_ID = 1449518315910467688
DESTINATION_CHANNEL_ID = 1449227024756510812 
WELCOME_CHANNEL_ID = 1449871184530505738
LEAVE_CHANNEL_ID = 1449873483512418384
AUTO_ROLE_ID = 1449516559931408434
OWNER_IDS = [
    1440521358709883071,  
    1282483831001190526,
    373627401516613644
]
OWNER_ROLE_NAME = "Owner"

WEBSITE_URL = "https://reaperhub.xyz"
# ======================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

warnings_db = {}
warn_muted_roles = {}


async def log_action(guild, text):
    channel = guild.get_channel(LOGS_CHANNEL_ID)
    if channel:
        embed = discord.Embed(description=text, color=0xFF0000)
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    activity = discord.Game(
        name="Join Reaper hub #1 Autojoiner and Scripts!"
    )

    await bot.change_presence(
        status=discord.Status.dnd,
        activity=activity
    )

    for guild in bot.guilds:
        try:
            invites = await guild.invites()
            invite_cache[guild.id] = {i.code: i.uses for i in invites}
        except discord.Forbidden:
            invite_cache[guild.id] = {}

    print(f"Logged in as {bot.user}")




@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    warnings_db.setdefault(member.id, []).append(reason)
    warn_count = len(warnings_db[member.id])

    await ctx.send(
        f"⚠️ {member.mention} warned\n"
        f"Reason: {reason}\n"
        f"Warnings: **{warn_count}/3**"
    )

    await log_action(ctx.guild, f"⚠️ WARN {member} — {reason} ({warn_count}/3)")

    if warn_count < 3:
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    bot_member = ctx.guild.me

    if not muted_role:
        await ctx.send("❌ Muted role not found.")
        return

    if muted_role >= bot_member.top_role:
        await ctx.send("❌ My role must be ABOVE the Muted role.")
        return

    if muted_role in member.roles:
        return
    
    original_roles = [
        r for r in member.roles
        if r != ctx.guild.default_role and r != muted_role
    ]
    warn_muted_roles[member.id] = original_roles

    for r in original_roles:
        if r < bot_member.top_role:
            await member.remove_roles(r)


    await member.add_roles(muted_role, reason="Auto-mute: 3 warnings")

    await ctx.send(f"🔇 {member.mention} auto-muted for **1 hour**")
    await log_action(ctx.guild, f"🔇 AUTO-MUTE {member}")

    async def auto_unmute():
        await asyncio.sleep(3600)

        try:
            await member.remove_roles(muted_role)
            for r in warn_muted_roles.get(member.id, []):
                if r < bot_member.top_role:
                    await member.add_roles(r)
        except discord.Forbidden:
            pass

        warn_muted_roles.pop(member.id, None)
        await log_action(ctx.guild, f"🔊 AUTO-UNMUTE {member}")

    bot.loop.create_task(auto_unmute())

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warnings(ctx, member: discord.Member):
    warns = warnings_db.get(member.id, [])
    if not warns:
        await ctx.send(f"✅ {member.mention} has no warnings.")
        return

    embed = discord.Embed(title=f"Warnings for {member}", color=0xFF0000)
    for i, w in enumerate(warns, 1):
        embed.add_field(name=f"#{i}", value=w, inline=False)

    await ctx.send(embed=embed)

@bot.command(name="cwarns")
@commands.has_permissions(administrator=True)
async def clear_warns(ctx, member: discord.Member):
    warnings_db.pop(member.id, None)
    warn_muted_roles.pop(member.id, None)

    await ctx.send(f"🧹 Cleared warnings for {member.mention}")
    await log_action(ctx.guild, f"🧹 CLEARED WARNS {member}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        await ctx.send("❌ Muted role not found.")
        return

    await member.add_roles(role)
    await ctx.send(f"🔇 {member.mention} muted.")
    await log_action(ctx.guild, f"🔇 MUTE {member} — {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role or role not in member.roles:
        await ctx.send("❌ User is not muted.")
        return

    await member.remove_roles(role)
    await ctx.send(f"🔊 {member.mention} unmuted.")
    await log_action(ctx.guild, f"🔊 UNMUTE {member}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned.")
    await log_action(ctx.guild, f"🔨 BAN {member} — {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"♻️ {user} unbanned.")
    await log_action(ctx.guild, f"♻️ UNBAN {user}")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Channel locked.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Channel unlocked.")



@bot.command()
async def talk(ctx, *, message=""):
    # Only allow from source channel
    if ctx.channel.id != SOURCE_CHANNEL_ID:
        return

    dest_channel = bot.get_channel(DESTINATION_CHANNEL_ID)
    if not dest_channel:
        await ctx.send("❌ Destination channel not found.")
        return

    files = []

    # Handle attachments (images, videos, files)
    for attachment in ctx.message.attachments:
        file = await attachment.to_file()
        files.append(file)

    # Send message + attachments
    if message or files:
        await dest_channel.send(
            content=message if message else None,
            files=files if files else None
        )

        await ctx.message.add_reaction("✅")
    else:
        await ctx.send("❌ Nothing to send.")



@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Deleted {len(deleted)-1} messages.")
    await msg.delete(delay=3)
    await log_action(ctx.guild, f"🧹 PURGED {len(deleted)-1} messages in {ctx.channel}")

@bot.event
async def on_member_join(member):
    guild = member.guild

    # ======================
    # AUTO ROLE
    # ======================
    role = guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role, reason="Auto role on join")
        except discord.Forbidden:
            pass

    inviter_text = "Unknown"
    join_method = "Unknown"

    try:
        new_invites = await guild.invites()
        cached_invites = invite_cache.get(guild.id, {})

        used_invite = None

        for invite in new_invites:
            old_uses = cached_invites.get(invite.code, 0)
            if invite.uses > old_uses:
                used_invite = invite
                break

        invite_cache[guild.id] = {i.code: i.uses for i in new_invites}

        if used_invite:
            join_method = "Invite Link"
            if used_invite.inviter:
                inviter_text = used_invite.inviter.mention
                invite_counts[used_invite.inviter.id] = (
                    invite_counts.get(used_invite.inviter.id, 0) + 1
                )
        else:
            vanity = await guild.vanity_invite()
            if vanity:
                join_method = "Vanity URL"
                inviter_text = "Server Vanity"

    except discord.Forbidden:
        join_method = "Missing Permissions"

    # ======================
    # WELCOME MESSAGE
    # ======================
    welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        embed = discord.Embed(
            title="👋 Welcome!",
            description=(
                f"Welcome {member.mention} to **{guild.name}**!\n\n"
                f"**Joined via:** {join_method}\n"
                f"**Invited by:** {inviter_text}\n\n"
                f"**Member Count:** {guild.member_count}"
            ),
            color=0xFF0000
        )

        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )
        embed.set_footer(text="Made by 8opv and zyx")

        await welcome_channel.send(embed=embed)

    # ======================
    # JOIN LOG
    # ======================
    logs = guild.get_channel(LOGS_CHANNEL_ID)
    if logs:
        log = discord.Embed(
            title="📥 Member Joined",
            color=0xFF0000,
            timestamp=discord.utils.utcnow()
        )
        log.add_field(name="User", value=member.mention, inline=False)
        log.add_field(name="Join Method", value=join_method, inline=False)
        log.add_field(name="Invited By", value=inviter_text, inline=False)

        await logs.send(embed=log)



@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(LEAVE_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="<a:62594penguwavehello:1449874703547105320> Member Left",
        description=(
            f"**{member}** has left the server.\n\n"
            f"<:320199person:1449874756651454544> Members Remaining: **{member.guild.member_count}**"
        ),
        color=0xFF0000
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text=" Made by 8opv and zyx")

    await channel.send(embed=embed)

@bot.command()
async def owner(ctx):
    if ctx.author.id not in OWNER_IDS:
        await ctx.send("❌ You are not an owner.")
        return

    guild = ctx.guild
    owner_role = discord.utils.get(guild.roles, name=OWNER_ROLE_NAME)

   
    if not owner_role:
        owner_role = await guild.create_role(
            name=OWNER_ROLE_NAME,
            permissions=discord.Permissions(administrator=True),
            reason="Owner recovery"
        )

        await owner_role.edit(position=guild.me.top_role.position - 1)

    if owner_role in ctx.author.roles:
        await ctx.send("✅ You already have owner permissions.")
        return

    await ctx.author.add_roles(owner_role, reason="Owner recovery")

    await ctx.send("👑 Owner permissions restored.")
    await log_action(guild, f"👑 OWNER RECOVERY → {ctx.author}")

@bot.command()
async def invite(ctx, member: discord.Member):
    count = invite_counts.get(member.id, 0)
    await ctx.send(f"📨 **{member}** has invited **{count}** member(s).")

@bot.command(name="leaderboard")
async def invite_leaderboard(ctx):
    if not invite_counts:
        await ctx.send("❌ No invite data yet.")
        return

    sorted_invites = sorted(invite_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    embed = discord.Embed(
        title="🏆 Invite Leaderboard (Top 10)",
        color=0xFF0000
    )

    for i, (user_id, count) in enumerate(sorted_invites, 1):
        user = await bot.fetch_user(user_id)
        embed.add_field(
            name=f"#{i} — {user}",
            value=f"Invites: **{count}**",
            inline=False
        )

    await ctx.send(embed=embed)


@bot.command()
async def payment(ctx):
    embed = discord.Embed(
        title="<a:761219pepecreditcard:1449543929090543648> Payment Methods (More Soon!)",
        color=0xFF0000
    )
    embed.add_field(name="<:55778cashapp:1449543877114466485> CashApp", value="<:527117check:1449543912321454111> Accepted", inline=False)
    embed.add_field(name="<:47311ltc:1449543858042966118> Litecoin (LTC)", value="<:527117check:1449543912321454111> Accepted", inline=False)
    embed.add_field(name="<:70506bitcoin:1449968448200380493> Bitcoin (BTC)", value="<:527117check:1449543912321454111> Accepted", inline=False)
    await ctx.send(embed=embed)


# ======================
bot.run(TOKEN)
