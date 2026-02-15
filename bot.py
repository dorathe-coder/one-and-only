#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Video Downloader Bot
Author: Custom Bot by Your Name
"""

import os
import logging
import asyncio
import re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
from helpers import download_video, extract_links_from_txt, extract_links_from_pdf, get_video_info, cleanup_downloads
from config import Config
from database import Database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Bot
bot = Client(
    "video_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Initialize Database
db = Database()

# User settings storage (in-memory for free hosting)
user_settings = {}

# Stats
stats = {
    'total_users': 0,
    'total_videos': 0,
    'total_downloads': 0
}


def get_user_setting(user_id, key, default=None):
    """Get user specific setting"""
    if user_id not in user_settings:
        user_settings[user_id] = {}
    return user_settings[user_id].get(key, default)


def set_user_setting(user_id, key, value):
    """Set user specific setting"""
    if user_id not in user_settings:
        user_settings[user_id] = {}
    user_settings[user_id][key] = value


def is_authorized(user_id):
    """Check if user is authorized"""
    if user_id == Config.OWNER_ID:
        return True
    return user_id in Config.AUTH_USERS


@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Start command handler"""
    user_id = message.from_user.id
    
    # Add to database
    db.add_user(user_id, message.from_user.first_name)
    
    welcome_text = f"""
👋 **Welcome {message.from_user.first_name}!**

🎥 **Universal Video Downloader Bot**

**📝 How to Use:**
1. Send me a `.txt` file with video links
2. I'll extract and download all videos
3. Videos will be uploaded here or to your channel

**⚙️ Commands:**
/settings - Configure bot settings
/help - Get detailed help
/stats - View bot statistics
/about - About this bot

**💡 Supported Platforms:**
✅ YouTube, Vimeo, Dailymotion
✅ Classplus, Apna College
✅ Instagram, Facebook, Twitter
✅ And many more...

Made with ❤️ by {Config.DEVELOPER_NAME}
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ])
    
    await message.reply_text(welcome_text, reply_markup=keyboard)


@bot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Help command handler"""
    help_text = """
📚 **Detailed Help Guide**

**🎯 Basic Usage:**

**Method 1: Text File**
• Create a `.txt` file with video links (one per line)
• Send the file to me
• I'll process all links automatically

**Method 2: Direct Link**
• Send video URL directly
• Bot will download and send

**⚙️ Settings Commands:**

`/set_thumbnail <image>` - Set custom thumbnail
`/remove_thumbnail` - Remove thumbnail
`/set_channel @username` - Set upload channel
`/remove_channel` - Remove channel
`/set_caption <text>` - Set custom caption
`/set_quality <quality>` - Set video quality (360/480/720/1080)

**👨‍💼 Owner Commands:**
`/broadcast <message>` - Send message to all users
`/stats` - Detailed statistics
`/add_user <user_id>` - Authorize user
`/remove_user <user_id>` - Deauthorize user

**📝 Text File Format:**

```
https://youtube.com/watch?v=xxxxx
Title: My Video 1

https://vimeo.com/xxxxx
Title: My Video 2
```

**💡 Tips:**
• Maximum file size: 2GB (Telegram limit)
• Batch processing: Up to 50 links per file
• Use /settings to customize bot behavior

Need help? Contact: {Config.SUPPORT_CONTACT}
"""
    
    await message.reply_text(help_text)


@bot.on_message(filters.command("settings"))
async def settings_command(client: Client, message: Message):
    """Settings command handler"""
    user_id = message.from_user.id
    
    thumbnail = get_user_setting(user_id, 'thumbnail')
    channel = get_user_setting(user_id, 'channel')
    caption = get_user_setting(user_id, 'caption')
    quality = get_user_setting(user_id, 'quality', '720')
    
    settings_text = f"""
⚙️ **Your Current Settings**

**🖼️ Thumbnail:** {'✅ Set' if thumbnail else '❌ Not Set'}
**📢 Channel:** {channel if channel else '❌ Not Set'}
**📝 Caption:** {'✅ Custom' if caption else '❌ Default'}
**🎬 Quality:** {quality}p

**Quick Actions:**
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼️ Set Thumbnail", callback_data="set_thumb"),
            InlineKeyboardButton("❌ Remove Thumb", callback_data="remove_thumb")
        ],
        [
            InlineKeyboardButton("📢 Set Channel", callback_data="set_channel"),
            InlineKeyboardButton("❌ Remove Channel", callback_data="remove_channel")
        ],
        [
            InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
            InlineKeyboardButton("❌ Remove Caption", callback_data="remove_caption")
        ],
        [
            InlineKeyboardButton("🎬 360p", callback_data="quality_360"),
            InlineKeyboardButton("🎬 480p", callback_data="quality_480"),
            InlineKeyboardButton("🎬 720p", callback_data="quality_720"),
            InlineKeyboardButton("🎬 1080p", callback_data="quality_1080")
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ])
    
    await message.reply_text(settings_text, reply_markup=keyboard)


@bot.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    """Stats command handler"""
    user_id = message.from_user.id
    
    if user_id != Config.OWNER_ID:
        await message.reply_text("⚠️ This command is only for owner!")
        return
    
    total_users = db.get_total_users()
    
    stats_text = f"""
📊 **Bot Statistics**

👥 **Total Users:** {total_users}
🎥 **Videos Processed:** {stats['total_videos']}
📥 **Total Downloads:** {stats['total_downloads']}

⏰ **Uptime:** Running smoothly
🔥 **Status:** Active

🚀 **Server:** Render.com (Free Tier)
💾 **Storage:** Temporary (Auto-cleanup)
"""
    
    await message.reply_text(stats_text)


@bot.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    """About command handler"""
    about_text = f"""
ℹ️ **About This Bot**

**🤖 Bot Name:** Universal Video Downloader
**👨‍💻 Developer:** {Config.DEVELOPER_NAME}
**📅 Version:** 2.0.0
**🔧 Framework:** Pyrogram + yt-dlp

**✨ Features:**
✅ Multi-platform support
✅ Batch processing
✅ Custom thumbnails
✅ Channel posting
✅ High-speed uploads
✅ 100% Free

**🔗 Source Code:** GitHub.com
**💬 Support:** {Config.SUPPORT_CONTACT}

**⚖️ Disclaimer:**
This bot is for educational purposes only.
Respect copyright laws and terms of service.

Made with ❤️ using Python
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Home", callback_data="start")]
    ])
    
    await message.reply_text(about_text, reply_markup=keyboard)


@bot.on_message(filters.document)
async def handle_document(client: Client, message: Message):
    """Handle text and PDF file uploads"""
    user_id = message.from_user.id
    
    if not is_authorized(user_id):
        await message.reply_text("⚠️ You are not authorized to use this bot!\nContact admin for access.")
        return
    
    file = message.document
    
    # Check if it's a text or PDF file
    is_txt = file.file_name.endswith('.txt')
    is_pdf = file.file_name.endswith('.pdf')
    
    if not (is_txt or is_pdf):
        await message.reply_text("⚠️ Please send a `.txt` or `.pdf` file containing video links!")
        return
    
    # Download the file
    status = await message.reply_text(f"📥 Downloading {file.file_name}...")
    
    try:
        file_path = await message.download()
        await status.edit_text("🔍 Extracting video links...")
        
        # Extract links based on file type
        if is_txt:
            links = extract_links_from_txt(file_path)
        else:  # PDF
            links = extract_links_from_pdf(file_path)
        
        if not links:
            await status.edit_text(f"❌ No valid video links found in the {file.file_name}!")
            os.remove(file_path)
            return
        
        await status.edit_text(f"✅ Found {len(links)} video link(s)!\n\n🎬 Starting download process...")
        
        # Get user settings
        thumbnail = get_user_setting(user_id, 'thumbnail')
        channel = get_user_setting(user_id, 'channel')
        caption_template = get_user_setting(user_id, 'caption')
        quality = get_user_setting(user_id, 'quality', '720')
        
        # Process each link
        successful = 0
        failed = 0
        
        for idx, link_data in enumerate(links, 1):
            try:
                url = link_data['url']
                title = link_data.get('title', f'Video_{idx}')
                
                progress_msg = await message.reply_text(
                    f"📥 **Processing {idx}/{len(links)}**\n"
                    f"🎬 **Title:** {title[:50]}...\n"
                    f"🔗 **URL:** {url[:50]}...\n\n"
                    f"⏳ Downloading..."
                )
                
                # Download video
                video_path = await download_video(url, title, quality, progress_msg)
                
                if not video_path:
                    await progress_msg.edit_text(f"❌ Failed: {title[:50]}...")
                    failed += 1
                    continue
                
                # Prepare caption
                if caption_template:
                    caption = caption_template.replace('{title}', title).replace('{index}', str(idx))
                else:
                    caption = f"🎬 **{title}**\n\n📥 Downloaded by @{bot.me.username}\n💝 Made by {Config.DEVELOPER_NAME}"
                
                # Upload video
                await progress_msg.edit_text(f"📤 Uploading {title[:30]}...")
                
                target_chat = channel if channel else message.chat.id
                
                await client.send_video(
                    chat_id=target_chat,
                    video=video_path,
                    caption=caption,
                    thumb=thumbnail,
                    supports_streaming=True
                )
                
                await progress_msg.edit_text(f"✅ Uploaded: {title[:50]}...")
                successful += 1
                
                # Cleanup
                if os.path.exists(video_path):
                    os.remove(video_path)
                
                # Update stats
                stats['total_videos'] += 1
                stats['total_downloads'] += 1
                db.increment_downloads(user_id)
                
                # Small delay
                await asyncio.sleep(2)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                logger.error(f"Error processing link {idx}: {str(e)}")
                failed += 1
        
        # Cleanup text file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Final summary
        summary = f"✅ **Process Complete!**\n\n"
        summary += f"📊 **Summary:**\n"
        summary += f"✅ Successful: {successful}\n"
        summary += f"❌ Failed: {failed}\n"
        summary += f"📁 Total: {len(links)}"
        
        await status.edit_text(summary)
        
    except Exception as e:
        logger.error(f"Error handling document: {str(e)}")
        await status.edit_text(f"❌ Error: {str(e)}")


@bot.on_message(filters.text & filters.regex(r'https?://'))
async def handle_direct_link(client: Client, message: Message):
    """Handle direct video links"""
    user_id = message.from_user.id
    
    if not is_authorized(user_id):
        await message.reply_text("⚠️ You are not authorized to use this bot!")
        return
    
    url = message.text.strip()
    
    status = await message.reply_text("🔍 Analyzing link...")
    
    try:
        # Get user settings
        thumbnail = get_user_setting(user_id, 'thumbnail')
        channel = get_user_setting(user_id, 'channel')
        caption_template = get_user_setting(user_id, 'caption')
        quality = get_user_setting(user_id, 'quality', '720')
        
        # Download video
        await status.edit_text("📥 Downloading video...")
        video_path = await download_video(url, quality, status)
        
        if not video_path:
            await status.edit_text("❌ Failed to download video!")
            return
        
        # Get video info
        title = os.path.basename(video_path).replace('.mp4', '')
        
        # Prepare caption
        if caption_template:
            caption = caption_template.replace('{title}', title)
        else:
            caption = f"🎬 **{title}**\n\n📥 Downloaded by @{bot.me.username}\n💝 Made by {Config.DEVELOPER_NAME}"
        
        # Upload video
        await status.edit_text("📤 Uploading video...")
        
        target_chat = channel if channel else message.chat.id
        
        await client.send_video(
            chat_id=target_chat,
            video=video_path,
            caption=caption,
            thumb=thumbnail,
            supports_streaming=True
        )
        
        await status.edit_text("✅ Video uploaded successfully!")
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        
        # Update stats
        stats['total_videos'] += 1
        stats['total_downloads'] += 1
        
    except Exception as e:
        logger.error(f"Error handling direct link: {str(e)}")
        await status.edit_text(f"❌ Error: {str(e)}")


@bot.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    """Handle callback queries"""
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "start":
        await callback.message.delete()
        await start_command(client, callback.message)
    
    elif data == "settings":
        await callback.message.delete()
        await settings_command(client, callback.message)
    
    elif data == "help":
        await callback.message.delete()
        await help_command(client, callback.message)
    
    elif data == "stats":
        await callback.message.delete()
        await stats_command(client, callback.message)
    
    elif data == "about":
        await callback.message.delete()
        await about_command(client, callback.message)
    
    elif data == "set_thumb":
        await callback.message.edit_text(
            "🖼️ **Set Thumbnail**\n\n"
            "Please send me an image to set as thumbnail.\n"
            "Send /cancel to cancel."
        )
    
    elif data == "remove_thumb":
        set_user_setting(user_id, 'thumbnail', None)
        await callback.answer("✅ Thumbnail removed!", show_alert=True)
    
    elif data == "set_channel":
        await callback.message.edit_text(
            "📢 **Set Channel**\n\n"
            "Please send channel username (with @)\n"
            "Example: @mychannel\n\n"
            "Send /cancel to cancel."
        )
    
    elif data == "remove_channel":
        set_user_setting(user_id, 'channel', None)
        await callback.answer("✅ Channel removed!", show_alert=True)
    
    elif data == "set_caption":
        await callback.message.edit_text(
            "📝 **Set Custom Caption**\n\n"
            "Send your custom caption.\n"
            "Use {title} for video title\n"
            "Use {index} for video number\n\n"
            "Example:\n`🎬 {title}\n📥 Video #{index}`\n\n"
            "Send /cancel to cancel."
        )
    
    elif data == "remove_caption":
        set_user_setting(user_id, 'caption', None)
        await callback.answer("✅ Caption removed!", show_alert=True)
    
    elif data.startswith("quality_"):
        quality = data.split("_")[1]
        set_user_setting(user_id, 'quality', quality)
        await callback.answer(f"✅ Quality set to {quality}p", show_alert=True)


async def upload_progress(current, total, message, title):
    """Upload progress callback"""
    try:
        percentage = (current / total) * 100
        bar_length = 20
        filled = int(bar_length * current // total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        await message.edit_text(
            f"📤 **Uploading: {title}**\n\n"
            f"Progress: {percentage:.1f}%\n"
            f"{bar}\n"
            f"📊 {current / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB"
        )
    except:
        pass


# Owner commands
@bot.on_message(filters.command("broadcast") & filters.user(Config.OWNER_ID))
async def broadcast_command(client: Client, message: Message):
    """Broadcast message to all users"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /broadcast <message>")
        return
    
    broadcast_msg = message.text.split(None, 1)[1]
    users = db.get_all_users()
    
    success = 0
    failed = 0
    
    status = await message.reply_text(f"📡 Broadcasting to {len(users)} users...")
    
    for user_id in users:
        try:
            await client.send_message(user_id, broadcast_msg)
            success += 1
        except:
            failed += 1
        
        await asyncio.sleep(0.5)
    
    await status.edit_text(
        f"✅ Broadcast Complete!\n\n"
        f"Success: {success}\n"
        f"Failed: {failed}"
    )


# Start the bot
if __name__ == "__main__":
    logger.info("🚀 Bot starting...")
    bot.run()
