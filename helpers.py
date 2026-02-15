#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for video downloading with DRM support
Supports: YouTube, Testbook, Classplus, Appx, and 1000+ platforms
"""

import os
import re
import asyncio
import logging
import subprocess
import json
from typing import List, Dict, Optional
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

# Check if N_m3u8DL-RE is available
N_M3U8DL_AVAILABLE = False
try:
    result = subprocess.run(['N_m3u8DL-RE', '--version'], 
                          capture_output=True, timeout=5)
    N_M3U8DL_AVAILABLE = result.returncode == 0
    if N_M3U8DL_AVAILABLE:
        logger.info("✅ N_m3u8DL-RE is available - DRM support enabled")
except:
    logger.warning("⚠️ N_m3u8DL-RE not found - using yt-dlp only")


def extract_links_from_txt(file_path: str) -> List[Dict[str, str]]:
    """
    Extract video links from text file
    
    Supported formats:
    1. Title:URL (Classplus/Testbook format)
    2. URL on separate line with optional title
    3. Mixed format
    """
    links = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Format: Title:URL
            if ':http' in line:
                # Find where URL starts
                url_start = line.find('http')
                if url_start > 0:
                    title = line[:url_start-1].strip()
                    # Remove colon separator
                    if title.endswith(':'):
                        title = title[:-1].strip()
                    url = line[url_start:].strip()
                    
                    links.append({
                        'url': url,
                        'title': title or f'Video_{len(links) + 1}'
                    })
                    continue
            
            # Format: Just URL
            if line.startswith('http://') or line.startswith('https://'):
                links.append({
                    'url': line,
                    'title': f'Video_{len(links) + 1}'
                })
        
        logger.info(f"✅ Extracted {len(links)} links from {file_path}")
        return links
        
    except Exception as e:
        logger.error(f"❌ Error extracting links: {str(e)}")
        return []


def extract_links_from_pdf(file_path: str) -> List[Dict[str, str]]:
    """Extract links from PDF file"""
    links = []
    
    try:
        import PyPDF2
        
        with open(file_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                
                # Extract URLs
                urls = re.findall(r'https?://[^\s]+', text)
                
                for url in urls:
                    links.append({
                        'url': url.strip(),
                        'title': f'PDF_Page{page_num}_Video_{len(links) + 1}'
                    })
        
        logger.info(f"✅ Extracted {len(links)} links from PDF")
        return links
        
    except ImportError:
        logger.error("❌ PyPDF2 not installed - PDF support disabled")
        return []
    except Exception as e:
        logger.error(f"❌ Error extracting from PDF: {str(e)}")
        return []


def sanitize_filename(filename: str) -> str:
    """Sanitize filename"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove extra spaces
    filename = re.sub(r'\s+', ' ', filename).strip()
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename or "video"


def is_drm_protected(url: str) -> bool:
    """Check if URL is from DRM-protected platform"""
    drm_platforms = [
        'testbook.com',
        'classplusapp.com',
        'appx.com',
        'drm',
        '/drm/',
        'encrypted'
    ]
    
    url_lower = url.lower()
    return any(platform in url_lower for platform in drm_platforms)


async def download_with_n_m3u8dl(url: str, output_path: str, 
                                  quality: str = "720",
                                  progress_callback=None) -> Optional[str]:
    """
    Download video using N_m3u8DL-RE (DRM support)
    """
    try:
        output_file = f"{output_path}.mp4"
        
        # N_m3u8DL-RE command
        cmd = [
            'N_m3u8DL-RE',
            url,
            '--save-name', os.path.basename(output_path),
            '--save-dir', os.path.dirname(output_path),
            '--tmp-dir', Config.DOWNLOAD_PATH,
            '--thread-count', '16',
            '--download-retry-count', '10',
            '--auto-select',
            '--check-segments-count', 'false',
            '--binary-merge',
            '--log-level', 'INFO'
        ]
        
        logger.info(f"📥 Downloading with N_m3u8DL-RE: {url[:50]}...")
        
        # Run command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Find output file
            for ext in ['.mp4', '.mkv', '.ts']:
                test_file = f"{output_path}{ext}"
                if os.path.exists(test_file):
                    logger.info(f"✅ Downloaded: {test_file}")
                    return test_file
            
            logger.error("❌ Output file not found after download")
            return None
        else:
            error_msg = stderr.decode('utf-8', errors='ignore')
            logger.error(f"❌ N_m3u8DL-RE failed: {error_msg[:200]}")
            return None
            
    except Exception as e:
        logger.error(f"❌ N_m3u8DL-RE error: {str(e)}")
        return None


async def download_with_ytdlp(url: str, output_path: str,
                               quality: str = "720",
                               progress_callback=None) -> Optional[str]:
    """
    Download video using yt-dlp
    """
    try:
        from yt_dlp import YoutubeDL
        
        quality_format = Config.QUALITY_OPTIONS.get(quality, 
                                                     Config.QUALITY_OPTIONS["720"])
        
        output_template = f"{output_path}.%(ext)s"
        
        ydl_opts = {
            'format': quality_format,
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'concurrent_fragment_downloads': 5,
            'retries': 10,
            'fragment_retries': 10,
            'socket_timeout': 30,
            'http_chunk_size': 10485760,
            'nocheckcertificate': True,
            'allow_unplayable_formats': False,
        }
        
        logger.info(f"📥 Downloading with yt-dlp: {url[:50]}...")
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if info:
                # Find downloaded file
                for ext in ['.mp4', '.mkv', '.webm']:
                    test_file = f"{output_path}{ext}"
                    if os.path.exists(test_file):
                        logger.info(f"✅ Downloaded: {test_file}")
                        return test_file
                
                logger.error("❌ Output file not found")
                return None
        
        return None
        
    except Exception as e:
        logger.error(f"❌ yt-dlp error: {str(e)}")
        return None


async def download_video(url: str, title: str = None,
                        quality: str = "720",
                        progress_message=None) -> Optional[str]:
    """
    Universal video downloader
    Auto-selects best method based on URL
    """
    try:
        # Sanitize title
        if not title:
            title = "video"
        title = sanitize_filename(title)
        
        # Output path (without extension)
        output_path = os.path.join(Config.DOWNLOAD_PATH, title)
        
        # Choose download method
        use_n_m3u8dl = N_M3U8DL_AVAILABLE and is_drm_protected(url)
        
        if use_n_m3u8dl:
            logger.info("🔐 DRM-protected link detected - using N_m3u8DL-RE")
            result = await download_with_n_m3u8dl(url, output_path, quality, 
                                                  progress_message)
        else:
            logger.info("📺 Standard link - using yt-dlp")
            result = await download_with_ytdlp(url, output_path, quality,
                                               progress_message)
        
        # Verify file
        if result and os.path.exists(result):
            file_size = os.path.getsize(result)
            
            if file_size > Config.MAX_FILE_SIZE:
                os.remove(result)
                raise Exception(f"File too large: {file_size / (1024**3):.2f} GB")
            
            logger.info(f"✅ Download complete: {file_size / (1024**2):.2f} MB")
            return result
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Download failed: {str(e)}")
        
        if progress_message:
            try:
                await progress_message.edit_text(f"❌ Download failed: {str(e)[:100]}")
            except:
                pass
        
        return None


def cleanup_downloads(keep_files: List[str] = None):
    """Clean up download directory"""
    try:
        keep_files = keep_files or []
        
        if os.path.exists(Config.DOWNLOAD_PATH):
            for file in os.listdir(Config.DOWNLOAD_PATH):
                file_path = os.path.join(Config.DOWNLOAD_PATH, file)
                
                if file_path not in keep_files:
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {str(e)}")
        
        logger.info("✅ Cleanup complete")
    except Exception as e:
        logger.error(f"❌ Cleanup error: {str(e)}")


# Supported platforms
SUPPORTED_PLATFORMS = [
    "YouTube", "Vimeo", "Dailymotion", "Instagram", "Facebook",
    "Twitter", "TikTok", "Reddit", "Twitch",
    "Testbook", "Classplus", "Appx", "Unacademy", "Physics Wallah",
    "And 1000+ more platforms"
]
