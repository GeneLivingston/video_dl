import yt_dlp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging
import os
from pathlib import Path
from typing import Optional
import time

class FriendlyLogger:
    def __init__(self):
        self.current_video_title: Optional[str] = None
        
    def debug(self, msg):
        pass
        
    def warning(self, msg):
        if "video id" in msg.lower():
            return
        print(f"⚠️  {msg}")
        
    def error(self, msg):
        print(f"❌ Oops! Something went wrong: {msg}")
    
    def info(self, msg):
        if "[download] Downloading video" in msg:
            self.current_video_title = msg.split('"')[1]
            print(f"\n🎥 Found video: {self.current_video_title}")
            print("⏳ Starting download...")
        elif "[download] Download completed" in msg:
            print(f"✅ Successfully saved '{self.current_video_title}' to your Videos folder!")
        elif "[download]" in msg and "%" in msg:
            # Extract percentage and format progress bar
            try:
                percent = float(msg.split()[1].replace('%', ''))
                self.print_progress_bar(percent)
            except:
                pass

    def print_progress_bar(self, percent):
        width = 40
        filled = int(width * percent / 100)
        bar = "█" * filled + "▒" * (width - filled)
        print(f"\r⏳ Downloading: |{bar}| {percent:.1f}%", end="")

def find_video_urls(page_url):
    """Find video URLs on a webpage that are legal to download."""
    print(f"🔍 Scanning webpage for videos...")
    
    try:
        response = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        video_urls = []
        
        # Look for standard video elements
        for video in soup.find_all('video'):
            if video.get('src'):
                video_urls.append(urljoin(page_url, video.get('src')))
            for source in video.find_all('source'):
                if source.get('src'):
                    video_urls.append(urljoin(page_url, source.get('src')))
        
        # Look for embedded videos
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if any(platform in src.lower() for platform in ['youtube.com', 'vimeo.com']):
                video_urls.append(src)
        
        if video_urls:
            print(f"✨ Found {len(video_urls)} video{'s' if len(video_urls) > 1 else ''}!")
        else:
            print("😕 No videos found on this page.")
            
        return video_urls
    
    except Exception as e:
        print(f"❌ Couldn't access the webpage: {str(e)}")
        return []

def download_video(video_url, output_path):
    """Download a video using yt-dlp with friendly output."""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'ignoreerrors': True,
        'logger': FriendlyLogger(),
        'progress_hooks': [],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            print()  # New line after progress bar
            
    except Exception as e:
        print(f"❌ Couldn't download the video: {str(e)}")

def main(webpage_url):
    """Main function to find and download videos from a webpage"""
    print("🎬 Video Downloader Starting Up!")
    print("--------------------------------")
    
    # Set output path to ~/Videos
    output_path = Path.home() / 'Videos'
    
    # Create Videos directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Videos will be saved to: {output_path}")
    print()
    
    video_urls = find_video_urls(webpage_url)
    
    if not video_urls:
        return
    
    print("\n🚀 Starting downloads...")
    for url in video_urls:
        download_video(url, output_path)
    
    print("\n✨ All done! Check your Videos folder for your downloads!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("👋 Please provide a webpage URL as an argument!")
        print("Example: python video_downloader.py https://example.com/page-with-video")


