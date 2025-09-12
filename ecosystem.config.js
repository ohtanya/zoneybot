module.exports = {
  apps: [{
    name: 'zoneybot',
    script: 'main.py',
    interpreter: 'python3',
    env: {
      DISCORD_BOT_TOKEN: 'your_actual_bot_token_here'
    },
    // Optional: Environment for production
    env_production: {
      NODE_ENV: 'production',
      DISCORD_BOT_TOKEN: 'your_production_bot_token_here'
    },
    // Restart settings
    watch: false,
    max_memory_restart: '1G',
    restart_delay: 4000,
    // Logging
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm Z'
  }]
}
