# Zoneybot 🌍

A Discord bot that helps server members coordinate across different timezones by allowing them to set and check each other's local times.

## Features

- **`/settimezone`** - Set your timezone (e.g., `/settimezone Europe/London`)
- **`/time`** - Check your own or another member's local time
- **`/times`** - See everyone's current local times at once
- **`/timezones`** - Search for available timezones by city or region

## Quick Start

### Prerequisites
- Python 3.7+
- Discord Bot Token
- PM2 (for production deployment)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd zoneybot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export DISCORD_BOT_TOKEN="your_bot_token_here"
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

## Production Deployment with PM2

1. **Install PM2:**
   ```bash
   npm install -g pm2
   ```

2. **Set your Discord bot token:**
   ```bash
   export DISCORD_BOT_TOKEN="your_actual_bot_token_here"
   ```

3. **Start with PM2 (first time):**
   ```bash
   pm2 start ecosystem.config.js
   ```

4. **After first setup, you can use:**
   ```bash
   pm2 start zoneybot    # Start the bot
   pm2 stop zoneybot     # Stop the bot  
   pm2 restart zoneybot  # Restart the bot
   pm2 delete zoneybot   # Remove from PM2
   ```

5. **Monitor the bot:**
   ```bash
   pm2 status
   pm2 logs zoneybot
   ```

### Alternative: Quick Start Script

You can also use the included start script:
```bash
./start.sh
```

## Bot Permissions

When inviting the bot to your Discord server, ensure it has:
- Send Messages
- Use Slash Commands
- Read Message History

## Environment Variables

- `DISCORD_BOT_TOKEN` - Your Discord bot token (required)

## File Structure

```
zoneybot/
├── main.py              # Main bot code
├── requirements.txt     # Python dependencies
├── ecosystem.config.js  # PM2 configuration
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Usage Examples

```
/settimezone America/New_York    # Set your timezone
/time @username                  # Check someone's time
/times                          # See everyone's times
/timezones london               # Search for London timezones
/timezones                      # See popular timezones
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this bot in your own servers!
