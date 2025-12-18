# Discord Bot - Reaper Hub

A feature-rich Discord bot with moderation, invite tracking, and member management capabilities.

## Features

- **Moderation Commands**
  - `!warn` - Warn users (auto-mute after 3 warnings)
  - `!mute` / `!unmute` - Mute/unmute users
  - `!ban` / `!unban` - Ban/unban users
  - `!purge` - Delete messages in bulk

- **Member Management**
  - Auto-role assignment on join
  - Welcome messages with invite tracking
  - Member join/leave logging
  - Invite leaderboard

- **Utility Commands**
  - `!lock` / `!unlock` - Lock/unlock channels
  - `!talk` - Send messages to another channel
  - `!leaderboard` - View invite rankings
  - `!payment` - Show payment methods
  - `!owner` - Owner recovery command

---

## Deployment

### Quick Start (Railway - Recommended)

Railway provides **$5 free credit/month** - perfect for Discord bots!

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial setup"
   git push origin main
   ```

2. **Deploy to Railway**
   - Go to https://railway.app/
   - Click **New Project** → **Deploy from GitHub**
   - Select this repository
   - Click **Deploy**

3. **Set Environment Variables**
   - In Railway dashboard → **Variables**
   - Add: `DISCORD_TOKEN` = Your bot token
   - Railway will restart automatically

4. **Verify**
   - Check Railway **Logs** - should see "Logged in as..."
   - Your bot should be online in Discord

See [RAILWAY_SETUP.md](./RAILWAY_SETUP.md) for detailed instructions.

### Other Hosting Options

- **Oracle Cloud** - 24GB RAM, 4 vCPUs free (best performance)
- **AWS EC2** - 750 hours/month free
- **Google Cloud Run** - 2M requests/month free

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
- Bot invited to your Discord server

### Local Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your bot token

# Run bot
python bot_secure.py
```

---

## Configuration

Edit these values in `bot_secure.py`:

```python
LOGS_CHANNEL_ID = 1449299029103087697          # Where to log actions
SOURCE_CHANNEL_ID = 1449518315910467688        # Source for !talk command
DESTINATION_CHANNEL_ID = 1449227024756510812   # Destination for !talk
WELCOME_CHANNEL_ID = 1449871184530505738       # Welcome messages
LEAVE_CHANNEL_ID = 1449873483512418384         # Leave notifications
AUTO_ROLE_ID = 1449516559931408434             # Auto-assigned role
OWNER_IDS = [...]                               # Owner user IDs
```

### Required Discord Roles

- **"Muted"** - For muting users (auto-created if missing)
- **"Owner"** - For owner recovery (optional)

### Required Bot Permissions

- Manage Roles
- Manage Channels
- Manage Messages
- Ban Members
- Moderate Members
- Send Messages
- Embed Links

---

## Commands

### Moderation

| Command | Permission | Description |
|---------|-----------|-------------|
| `!warn <user> [reason]` | Moderate Members | Warn a user (auto-mute after 3) |
| `!warnings <user>` | Moderate Members | View user warnings |
| `!cwarns <user>` | Administrator | Clear user warnings |
| `!mute <user> [reason]` | Manage Roles | Mute a user |
| `!unmute <user>` | Manage Roles | Unmute a user |
| `!ban <user> [reason]` | Ban Members | Ban a user |
| `!unban <user_id>` | Ban Members | Unban a user |

### Utility

| Command | Description |
|---------|-------------|
| `!lock` | Lock current channel |
| `!unlock` | Unlock current channel |
| `!talk [message]` | Send message to destination channel |
| `!purge <amount>` | Delete messages |
| `!invite <user>` | Show user's invite count |
| `!leaderboard` | Show top 10 inviters |
| `!payment` | Show payment methods |
| `!owner` | Owner recovery (owner only) |

---

## Features Explained

### Auto-Warning System
- Users get warned with `!warn`
- After 3 warnings, user is auto-muted for 1 hour
- Warnings are logged
- Clear warnings with `!cwarns`

### Invite Tracking
- Bot tracks which invite link was used
- Counts invites per user
- Shows in welcome message
- Leaderboard with `!leaderboard`

### Logging
- All moderation actions logged to LOGS_CHANNEL
- Timestamps on all logs
- Color-coded embeds for easy reading

### Member Management
- Auto-role on join
- Welcome messages with member count
- Leave notifications
- Invite tracking

---

## Environment Variables

Create a `.env` file:

```
DISCORD_TOKEN=your_bot_token_here
```

**Never commit `.env` to version control!**

---

## Troubleshooting

### Bot Not Starting
```
Check logs for error messages
Verify DISCORD_TOKEN is set correctly
Ensure bot has required permissions in Discord
```

### Commands Not Working
```
Bot needs proper Discord permissions
Check that required roles exist
Verify channel IDs are correct
```

### Bot Goes Offline
```
Check Railway/hosting provider status
Restart the bot
Check logs for crashes
```

---

## Support

- **Discord.py Documentation:** https://discordpy.readthedocs.io/
- **Discord Developer Portal:** https://discord.com/developers/
- **Railway Support:** https://docs.railway.app/

---

## License

This bot is provided as-is. Feel free to modify and use for your own servers.

---

## Credits

Made by 8opv and zyx

---

## Deployment Status

- ✅ Ready for Railway deployment
- ✅ Environment variables configured
- ✅ All dependencies in requirements.txt
- ✅ Procfile configured

Deploy now: https://railway.app/
