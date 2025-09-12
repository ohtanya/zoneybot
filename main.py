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
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
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

@bot.tree.command(name="time", description="Show local time for yourself or another member")
async def time(interaction: discord.Interaction, member: discord.Member = None):
    """Show local time for yourself or another member"""
    member = member or interaction.user
    tz = user_timezones.get(member.id)
    if tz:
        now = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M")
        await interaction.response.send_message(f"🕒 {BOT_NAME}: {member.display_name}'s local time: **{now}** ({tz})")
    else:
        await interaction.response.send_message(f"⚠️ {BOT_NAME}: {member.display_name} hasn't set a timezone yet. Use `/settimezone`")

@bot.tree.command(name="times", description="Show a list of all users and their local times")
async def times(interaction: discord.Interaction):
    """Show a list of all users and their local times"""
    if not user_timezones:
        await interaction.response.send_message(f"{BOT_NAME}: No users have set their timezone yet.")
        return

    lines = []
    for uid, tz in user_timezones.items():
        member = interaction.guild.get_member(uid)
        if member:
            now = datetime.now(pytz.timezone(tz)).strftime("%H:%M")
            lines.append(f"{member.display_name} — {now} ({tz})")
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
