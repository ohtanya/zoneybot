import discord
from discord.ext import commands
from datetime import datetime
import pytz
import os

# Get bot token from environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    print("❌ Error: DISCORD_BOT_TOKEN environment variable not set!")
    exit(1)

intents = discord.Intents.default()
# Remove message_content intent since we only use slash commands
# intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Store user timezones (replace with database for production)
user_timezones = {}

# Optional: Name to display in messages
BOT_NAME = "Zoneybot"

@bot.event
async def on_ready():
    print(f"✅ {BOT_NAME} is online as {bot.user}")
    try:
        # Just sync globally - guild sync was clearing commands
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} global slash command(s)")
        # Debug: print all synced command names
        for cmd in synced:
            print(f"   - {cmd.name}: {cmd.description}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name="settimezone", description="Set your timezone (e.g., America/Los_Angeles)")
async def settimezone(interaction: discord.Interaction, timezone: str):
    """Set your timezone"""
    try:
        pytz.timezone(timezone)  # validate
        user_timezones[interaction.user.id] = timezone
        await interaction.response.send_message(f"✅ {BOT_NAME}: Timezone set to `{timezone}` for {interaction.user.display_name}")
    except Exception:
        await interaction.response.send_message(
            f"❌ {BOT_NAME}: Invalid timezone `{timezone}`\n"
            f"Use `/timezones` to see available options or try formats like:\n"
            f"• `America/New_York`\n"
            f"• `Europe/London`\n"
            f"• `Asia/Tokyo`"
        )

@bot.tree.command(name="admintz", description="Admin: Set timezone for another user")
async def settimezone_admin(interaction: discord.Interaction, member: discord.Member, timezone: str):
    """Admin command to set timezone for another user"""
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(f"❌ {BOT_NAME}: You need administrator permissions to use this command.")
        return
    
    try:
        pytz.timezone(timezone)  # validate
        user_timezones[member.id] = timezone
        await interaction.response.send_message(f"✅ {BOT_NAME}: Timezone set to `{timezone}` for {member.display_name} (set by admin {interaction.user.display_name})")
    except Exception:
        await interaction.response.send_message(
            f"❌ {BOT_NAME}: Invalid timezone `{timezone}`\n"
            f"Use `/timezones` to see available options or try formats like:\n"
            f"• `America/New_York`\n"
            f"• `Europe/London`\n"
            f"• `Asia/Tokyo`"
        )

@bot.tree.command(name="time", description="Show local time for yourself or another member")
async def time(interaction: discord.Interaction, member: discord.Member = None):
    """Show local time for yourself or another member"""
    member = member or interaction.user
    target_tz = user_timezones.get(member.id)
    
    if not target_tz:
        await interaction.response.send_message(f"⚠️ {BOT_NAME}: {member.display_name} hasn't set a timezone yet. Use `/settimezone`")
        return
    
    # Get the target user's current time
    target_time = datetime.now(pytz.timezone(target_tz))
    
    # Get the requesting user's timezone for comparison
    requester_tz = user_timezones.get(interaction.user.id)
    
    # Format the time nicely
    time_24h = target_time.strftime("%Y-%m-%d %H:%M")
    time_12h = target_time.strftime("%-I:%M%p").lower()  # 4:46pm format
    
    # Determine day relative to requester
    day_suffix = ""
    if requester_tz:
        requester_time = datetime.now(pytz.timezone(requester_tz))
        target_date = target_time.date()
        requester_date = requester_time.date()
        
        if target_date > requester_date:
            day_suffix = " TOMORROW"
        elif target_date < requester_date:
            day_suffix = " YESTERDAY"
    
    await interaction.response.send_message(
        f"🕒 {BOT_NAME}: It's {time_24h} ({time_12h}{day_suffix}) for {member.display_name}."
    )

@bot.tree.command(name="times", description="Show a list of all users and their local times")
async def times(interaction: discord.Interaction):
    """Show a list of all users and their local times"""
    if not user_timezones:
        await interaction.response.send_message(f"{BOT_NAME}: No users have set their timezone yet.")
        return

    # Get requester's timezone for day comparison
    requester_tz = user_timezones.get(interaction.user.id)
    requester_time = None
    if requester_tz:
        requester_time = datetime.now(pytz.timezone(requester_tz))

    lines = []
    for uid, tz in user_timezones.items():
        member = interaction.guild.get_member(uid)
        if member:
            user_time = datetime.now(pytz.timezone(tz))
            time_12h = user_time.strftime("%-I:%M%p").lower()
            
            # Determine day suffix relative to requester
            day_suffix = ""
            if requester_time:
                user_date = user_time.date()
                requester_date = requester_time.date()
                
                if user_date > requester_date:
                    day_suffix = " tomorrow"
                elif user_date < requester_date:
                    day_suffix = " yesterday"
            
            lines.append(f"{member.display_name} — {time_12h}{day_suffix}")
    
    await interaction.response.send_message(f"**🌍 {BOT_NAME} Current Times:**\n" + "\n".join(lines))

@bot.tree.command(name="timezones", description="Search for available timezones by region or city")
async def timezones(interaction: discord.Interaction, search: str = None):
    """Show available timezones, optionally filtered by search term"""
    all_timezones = pytz.all_timezones
    
    if search:
        # Normalize search term - replace spaces with underscores for better matching
        search_normalized = search.replace(" ", "_")
        
        # Filter timezones that contain the search term (case-insensitive)
        # Try both original search and normalized version
        filtered_timezones = [tz for tz in all_timezones if 
                            search.lower() in tz.lower() or 
                            search_normalized.lower() in tz.lower()]
        
        if not filtered_timezones:
            await interaction.response.send_message(f"❌ No timezones found containing '{search}'. Try a city, country, or region name.")
            return
        
        # Limit results to prevent message being too long
        if len(filtered_timezones) > 20:
            filtered_timezones = filtered_timezones[:20]
            truncated_msg = f"\n*... and {len([tz for tz in all_timezones if search.lower() in tz.lower()]) - 20} more. Be more specific to narrow results.*"
        else:
            truncated_msg = ""
        
        timezone_list = "\n".join([f"• `{tz}`" for tz in sorted(filtered_timezones)])
        await interaction.response.send_message(
            f"🌍 **Timezones containing '{search}':**\n{timezone_list}{truncated_msg}"
        )
    else:
        # Show popular timezones by region
        popular_timezones = {
            "🇺🇸 **North America**": [
                "America/New_York", "America/Chicago", "America/Denver", 
                "America/Los_Angeles", "America/Toronto", "America/Vancouver"
            ],
            "🇪🇺 **Europe**": [
                "Europe/London", "Europe/Paris", "Europe/Berlin", 
                "Europe/Rome", "Europe/Madrid", "Europe/Amsterdam"
            ],
            "🌏 **Asia/Pacific**": [
                "Asia/Tokyo", "Asia/Shanghai", "Asia/Seoul", 
                "Asia/Mumbai", "Asia/Singapore", "Australia/Sydney"
            ],
            "🌍 **Other Regions**": [
                "Africa/Cairo", "America/Sao_Paulo", "Pacific/Auckland"
            ]
        }
        
        response = "🌍 **Popular Timezones:**\n\n"
        for region, zones in popular_timezones.items():
            response += f"{region}\n"
            response += "\n".join([f"• `{tz}`" for tz in zones])
            response += "\n\n"
        
        response += "💡 **Tips:**\n"
        response += "• Use `/timezones london` to search for specific cities\n"
        response += "• Use `/timezones america` to see all American timezones\n"
        response += "• Format: `Continent/City` (e.g., `Europe/London`)"
        
        await interaction.response.send_message(response)

bot.run(TOKEN)
