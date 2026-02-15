# 🎥 Universal Telegram Video Downloader Bot v2.0

Professional Telegram bot with **DRM support** for downloading videos from 1000+ platforms including Testbook, Classplus, Appx, and encrypted educational platforms.

## 🌟 Key Features

### ✅ DRM & Encryption Support
- **N_m3u8DL-RE** integration for encrypted streams
- **Testbook** ✅
- **Classplus** ✅
- **Appx** ✅
- Other DRM-protected platforms

### ✅ Multi-Format Support
- TXT files (video links)
- PDF files (extract links from PDFs)
- Direct URL sharing
- Batch processing (unlimited videos)

### ✅ Customization
- Custom thumbnails (set/remove)
- Custom captions with variables
- Quality selection (360p/480p/720p/1080p)
- Channel auto-posting
- Custom filenames

### ✅ Admin Features
- User authorization system
- Broadcast messages to all users
- Statistics tracking
- Ban/unban users
- Logs monitoring

### ✅ Smart Features
- Auto-detect DRM protection
- Fallback to yt-dlp for standard links
- Progress tracking
- Error handling & retry
- Auto cleanup

## 🚀 Quick Deploy

### Prerequisites
1. **Telegram API Credentials**
   - Get from: https://my.telegram.org
   - You need: API_ID, API_HASH

2. **Bot Token**
   - Get from: @BotFather on Telegram
   - Command: `/newbot`

3. **Your Telegram User ID**
   - Get from: @userinfobot
   - This will be your OWNER_ID

### Deploy to Render (100% Free)

#### Step 1: Fork Repository
1. Fork this repository to your GitHub
2. Or create new repository and upload files

#### Step 2: Sign Up on Render
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render

#### Step 3: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your repository
3. Configure:
   - Name: `telegram-video-bot`
   - Environment: `Python 3`
   - Build Command: (Auto-detected from render.yaml)
   - Start Command: `python bot.py`
   - Plan: **Free**

#### Step 4: Environment Variables
Add these in Render dashboard:

```bash
API_ID = YOUR_API_ID
API_HASH = YOUR_API_HASH
BOT_TOKEN = YOUR_BOT_TOKEN
OWNER_ID = YOUR_TELEGRAM_USER_ID
PYTHON_VERSION = 3.11.9
```

Optional:
```bash
DEVELOPER_NAME = Your Name
SUPPORT_CONTACT = @yourusername
MONGODB_URI = your_mongodb_uri
AUTH_USERS = 123456789,987654321
ENABLE_PUBLIC_USE = True
```

#### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 5-10 minutes
3. Check logs for "🚀 Bot starting..."
4. Test on Telegram with `/start`

## 📝 How to Use

### For Users

**1. Send TXT File**
```
Title:https://platform.com/video1.m3u8
Title:https://platform.com/video2.m3u8
```

**2. Send PDF File**
Bot will extract all video links from PDF

**3. Send Direct Link**
```
https://youtube.com/watch?v=xxxxx
```

**4. Configure Settings**
```
/settings
```

### Commands

**User Commands:**
- `/start` - Start the bot
- `/help` - Get help
- `/settings` - Configure bot
- `/stats` - View statistics
- `/about` - About bot

**Owner Commands:**
- `/broadcast <message>` - Message all users
- `/add_user <user_id>` - Authorize user
- `/remove_user <user_id>` - Remove user

### Settings Options

**Thumbnail:**
- Set custom thumbnail for videos
- Remove thumbnail

**Channel:**
- Set channel for auto-posting
- Bot must be admin in channel
- Remove channel setting

**Caption:**
- Custom caption with variables
- `{title}` - Video title
- `{index}` - Video number
- Example: `🎬 {title} | Video #{index}`

**Quality:**
- 360p - Small size, fast
- 480p - Medium quality
- 720p - HD (recommended) ⭐
- 1080p - Full HD (large files)

## 🎯 Supported Platforms

### Educational (with DRM)
- ✅ **Testbook**
- ✅ **Classplus**
- ✅ **Appx**
- ✅ Unacademy
- ✅ Physics Wallah
- ✅ Apna College
- ✅ Khan Academy

### Video Platforms
- ✅ YouTube
- ✅ Vimeo
- ✅ Dailymotion
- ✅ Instagram
- ✅ Facebook
- ✅ Twitter/X
- ✅ TikTok
- ✅ Reddit

### Indian OTT
- ✅ Hotstar
- ✅ Zee5
- ✅ SonyLIV
- ✅ Voot
- ✅ MX Player

**And 1000+ more platforms!**

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| API_ID | Telegram API ID | ✅ Yes | - |
| API_HASH | Telegram API Hash | ✅ Yes | - |
| BOT_TOKEN | Bot token from BotFather | ✅ Yes | - |
| OWNER_ID | Your Telegram user ID | ✅ Yes | - |
| PYTHON_VERSION | Python version | ❌ No | 3.11.9 |
| DEVELOPER_NAME | Your name | ❌ No | Your Name |
| MONGODB_URI | MongoDB connection | ❌ No | - |
| AUTH_USERS | Authorized user IDs | ❌ No | - |
| ENABLE_PUBLIC_USE | Allow public use | ❌ No | True |

## 🛠️ Technical Details

### Technologies Used
- **Pyrogram** - Telegram MTProto API
- **yt-dlp** - Universal video downloader
- **N_m3u8DL-RE** - DRM & M3U8 downloader
- **FFmpeg** - Video processing
- **MongoDB** - Database (optional)
- **Python 3.11** - Programming language

### Architecture
```
User → Telegram Bot → Download Manager
                    ├── DRM Detection
                    ├── N_m3u8DL-RE (DRM)
                    └── yt-dlp (Standard)
                    → Upload to Telegram
```

### File Structure
```
telegram-video-bot/
├── bot.py              # Main bot logic
├── config.py           # Configuration
├── helpers.py          # Download functions
├── database.py         # Database handler
├── requirements.txt    # Dependencies
├── render.yaml         # Render config
├── Procfile           # Process file
├── runtime.txt        # Python version
└── README.md          # Documentation
```

## 📊 Performance

- **Download Speed:** Up to 50 MB/s (depends on source)
- **Concurrent Downloads:** 3 videos simultaneously
- **Maximum File Size:** 2 GB (Telegram limit)
- **Batch Processing:** Unlimited videos per file
- **Uptime:** 24/7 on Render free tier (750 hours/month)

## 🔒 Security & Privacy

- ✅ No data stored permanently (optional MongoDB)
- ✅ Auto-cleanup of temporary files
- ✅ Secure environment variables
- ✅ Authorization system
- ✅ Session files encrypted

## ⚠️ Disclaimer

This bot is for **educational purposes only**. Users must:
- Respect copyright laws
- Follow platform terms of service
- Only download content they have rights to
- Use for personal/educational purposes only

The developers are not responsible for misuse of this software.

## 🐛 Troubleshooting

### Bot Not Responding
- Check if bot is running (Render dashboard)
- Verify environment variables
- Check logs for errors

### Download Fails
- Try lower quality (480p/720p)
- Check if link is still valid
- Some platforms may block downloads

### DRM Videos Not Working
- Ensure N_m3u8DL-RE is installed
- Check render.yaml build command
- View logs for specific errors

### Upload Fails
- File might be >2GB
- Use lower quality
- Check internet connection

## 📞 Support

- 🐛 **Issues:** GitHub Issues
- 💬 **Contact:** Check bot `/about` command
- 📖 **Docs:** This README

## 🙏 Credits

- **yt-dlp:** https://github.com/yt-dlp/yt-dlp
- **N_m3u8DL-RE:** https://github.com/nilaoda/N_m3u8DL-RE
- **Pyrogram:** https://github.com/pyrogram/pyrogram

## 📄 License

MIT License - See LICENSE file

---

Made with ❤️ for educational purposes

**Star ⭐ this repo if you find it useful!**
