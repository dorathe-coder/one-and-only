#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for Telegram Video Bot
"""

import os
from typing import List

class Config:
    """Bot configuration"""
    
    # Telegram API Credentials
    API_ID: int = int(os.environ.get("API_ID", "0"))
    API_HASH: str = os.environ.get("API_HASH", "")
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    
    # Owner Configuration
    OWNER_ID: int = int(os.environ.get("OWNER_ID", "0"))
    
    # Authorized Users (comma-separated user IDs)
    AUTH_USERS: List[int] = [int(x) for x in os.environ.get("AUTH_USERS", "").split(",") if x.strip()]
    
    # Bot Settings
    DEVELOPER_NAME: str = os.environ.get("DEVELOPER_NAME", "Your Name")
    SUPPORT_CONTACT: str = os.environ.get("SUPPORT_CONTACT", "@yourusername")
    
    # Download Settings
    DOWNLOAD_PATH: str = os.environ.get("DOWNLOAD_PATH", "./downloads/")
    MAX_FILE_SIZE: int = int(os.environ.get("MAX_FILE_SIZE", "2147483648"))  # 2GB in bytes
    
    # Video Quality Options
    QUALITY_OPTIONS = {
        "360": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "480": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    }
    
    # Default Settings
    DEFAULT_QUALITY: str = "720"
    DEFAULT_CAPTION: str = "🎬 Downloaded by Bot\n💝 Made with ❤️"
    
    # Database (Optional - MongoDB)
    MONGODB_URI: str = os.environ.get("MONGODB_URI", "")
    DATABASE_NAME: str = os.environ.get("DATABASE_NAME", "video_bot")
    
    # Rate Limiting
    MAX_CONCURRENT_DOWNLOADS: int = 3
    DELAY_BETWEEN_DOWNLOADS: int = 2  # seconds
    
    # Logging
    LOG_CHANNEL: int = int(os.environ.get("LOG_CHANNEL", "0"))  # Optional log channel ID
    
    # Features Toggle
    ENABLE_PUBLIC_USE: bool = os.environ.get("ENABLE_PUBLIC_USE", "True").lower() == "true"
    ENABLE_STATS: bool = os.environ.get("ENABLE_STATS", "True").lower() == "true"
    
    @staticmethod
    def validate():
        """Validate configuration"""
        if not Config.API_ID or Config.API_ID == 0:
            raise ValueError("API_ID is required!")
        
        if not Config.API_HASH:
            raise ValueError("API_HASH is required!")
        
        if not Config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required!")
        
        print("✅ Configuration validated successfully!")
        
        # Create download directory if not exists
        os.makedirs(Config.DOWNLOAD_PATH, exist_ok=True)


# Validate config on import
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("\n⚠️  Please set the following environment variables:")
    print("   - API_ID")
    print("   - API_HASH")
    print("   - BOT_TOKEN")
    print("   - OWNER_ID (your Telegram user ID)")
