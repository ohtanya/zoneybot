#!/bin/bash

# Zoneybot PM2 startup script
# This allows you to run: pm2 start zoneybot

# Check if DISCORD_BOT_TOKEN is set
if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "❌ Error: DISCORD_BOT_TOKEN environment variable not set!"
    echo "Set it with: export DISCORD_BOT_TOKEN='your_token_here'"
    exit 1
fi

# Start the bot with PM2
pm2 start main.py --name zoneybot --interpreter python3

echo "✅ Zoneybot started! Use 'pm2 logs zoneybot' to view logs."
