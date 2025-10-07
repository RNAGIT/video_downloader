"""
Simple Video Downloader - No Advanced Dependencies Required
Works with basic Python packages only
"""

from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import json
import threading
import time
import uuid
import random
import logging
import shutil
from datetime import datetime

# Check if aria2c is available for faster downloads
ARIA2C_AVAILABLE = shutil.which('aria2c') is not None

# Custom logger to suppress cookie errors
class CookieErrorFilter(logging.Filter):
    def filter(self, record):
        # Suppress Chrome cookie database errors
        if 'Could not copy Chrome cookie database' in record.getMessage():
            return False
        if 'cookie database' in record.getMessage().lower():
            return False
        return True

# Configure logging
logging.basicConfig(level=logging.INFO)
for handler in logging.root.handlers:
    handler.addFilter(CookieErrorFilter())

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Global storage for download progress
download_progress = {}
download_history = []

# CRITICAL FIX FOR RENDER: Use /tmp which is GUARANTEED writable
# Render's main filesystem may have permission issues, /tmp always works
is_cloud = os.environ.get('RENDER') or os.environ.get('HEROKU') or os.environ.get('RAILWAY')

if is_cloud:
    # On cloud platforms, use /tmp which is guaranteed writable
    DOWNLOADS_DIR = "/tmp/youtube_downloader_files"
    print(f"☁️ Cloud platform detected - using /tmp directory")
else:
    # Local development - use relative path
    DOWNLOADS_DIR = os.path.abspath("downloads")
    print(f"🏠 Local environment - using ./downloads")

def ensure_downloads_directory():
    """Ensure downloads directory exists with proper permissions"""
    global DOWNLOADS_DIR
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(DOWNLOADS_DIR, mode=0o777, exist_ok=True)
        
        # Test write access with a temporary file
        test_file = os.path.join(DOWNLOADS_DIR, '.test_write')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✅ Downloads directory is writable: {DOWNLOADS_DIR}")
        except Exception as e:
            print(f"❌ Cannot write to {DOWNLOADS_DIR}: {e}")
            # Force use /tmp as absolute last resort
            DOWNLOADS_DIR = "/tmp/video_downloads"
            os.makedirs(DOWNLOADS_DIR, mode=0o777, exist_ok=True)
            print(f"✅ Using emergency fallback: {DOWNLOADS_DIR}")
        
        print(f"📂 Final directory: {DOWNLOADS_DIR}")
        print(f"📂 Writable: {os.access(DOWNLOADS_DIR, os.W_OK)}")
        
    except Exception as e:
        print(f"❌ Fatal error setting up directory: {e}")
        # Absolute last resort
        DOWNLOADS_DIR = "/tmp"
        print(f"⚠️ Using system /tmp: {DOWNLOADS_DIR}")

# Initialize downloads directory
ensure_downloads_directory()

# History file
HISTORY_FILE = "download_history.json"

def load_history():
    global download_history
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                download_history = json.load(f)
    except:
        download_history = []

def save_history():
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(download_history, f, indent=2)
    except:
        pass

def download_video_task(url, format_choice, download_id):
    """Download video in background thread"""
    try:
        # Initialize progress
        download_progress[download_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Starting download...',
            'filename': '',
            'error': None
        }
        
        # Progress hook with filename tracking
        downloaded_filename = None
        
        def progress_hook(d):
            nonlocal downloaded_filename
            
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)

                if total and total > 0:
                    percent = min((downloaded / total) * 100, 100)
                    downloaded_mb = downloaded // (1024 * 1024)
                    total_mb = total // (1024 * 1024)

                    download_progress[download_id].update({
                        'status': 'downloading',
                        'progress': percent,
                        'message': f'Downloading: {int(percent)}% ({downloaded_mb}MB / {total_mb}MB)'
                    })
                else:
                    downloaded_mb = downloaded // (1024 * 1024)
                    download_progress[download_id].update({
                        'status': 'downloading',
                        'progress': 0,
                        'message': f'Downloading: {downloaded_mb}MB downloaded...'
                    })

            elif d['status'] == 'finished':
                # Track the downloaded filename - GET FULL PATH
                if 'filename' in d:
                    # Store FULL PATH not just basename
                    downloaded_filename = d['filename']
                    print(f"📁 Downloaded file (FULL PATH): {downloaded_filename}")
                    print(f"📁 File exists check: {os.path.exists(downloaded_filename)}")
                
                download_progress[download_id].update({
                    'status': 'finished',
                    'progress': 100,
                    'message': f'Download complete! Preparing file...'
                })

        # Prepare yt-dlp options with bot detection bypass and SSL fixes
        
        # Random user agents to avoid detection (updated with latest versions)
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0'
        ]
        
        # CRITICAL: Show exactly where files will be downloaded
        output_template = os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s')
        print(f"📥 Download will save to: {output_template}")
        print(f"📥 DOWNLOADS_DIR: {DOWNLOADS_DIR}")
        print(f"📥 Directory exists: {os.path.exists(DOWNLOADS_DIR)}")
        print(f"📥 Directory writable: {os.access(DOWNLOADS_DIR, os.W_OK)}")
        
        ydl_opts = {
            'outtmpl': output_template,
            'progress_hooks': [progress_hook],
            'postprocessors': [],
            'geo_bypass': True,
            'nocheckcertificate': True,
            'restrictfilenames': True,
            'noplaylist': True,
            'age_limit': None,
            'ignoreerrors': False,  # Don't ignore download errors, but ignore cookie errors
            'extract_flat': False,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs'],
                    'innertube_api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                    'innertube_client_version': '2.20231219.01.00',
                    'innertube_context': {
                        'client': {
                            'clientName': 'WEB',
                            'clientVersion': '2.20231219.01.00',
                        }
                    }
                }
            },
            'sleep_interval': random.uniform(1, 3),
            'max_sleep_interval': 8,
            'sleep_interval_subtitles': random.uniform(1, 2),
            'http_headers': {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            },
            'extractor_retries': 5,
            'fragment_retries': 5,
            'retries': 5,
            'no_color': True,
            'quiet': True,
            'no_warnings': True,
            # SSL and certificate fixes for cloud deployment
            'nocheckcertificate': True,
            'prefer_insecure': True,
            'legacy_server_connect': True,
            'source_address': '0.0.0.0',
            'socket_timeout': 60,
            'connect_timeout': 60,
            'http_chunk_size': 10485760,  # 10MB chunks
            'fragment_retries': 5,
            'retry_sleep_functions': {'http': lambda n: min(4 ** n, 120)},
            # Speed optimization settings
            'concurrent_fragment_downloads': 16,  # Download 16 fragments simultaneously
            'buffersize': 1024 * 1024 * 2,  # 2MB buffer
            'ratelimit': None,  # No rate limit
            'throttledratelimit': None,  # No throttled rate limit
            # External downloader for faster speeds (if aria2c is installed)
            'external_downloader': 'aria2c' if ARIA2C_AVAILABLE else None,
            'external_downloader_args': {
                'aria2c': [
                    '--max-connection-per-server=16',
                    '--split=16',
                    '--min-split-size=1M',
                    '--max-concurrent-downloads=16',
                    '--continue=true',
                    '--max-overall-download-limit=0',
                    '--max-download-limit=0',
                    '--file-allocation=none',
                ]
            } if ARIA2C_AVAILABLE else {},
            # Additional cloud-optimized settings
            'sleep_interval_requests': random.uniform(2, 5),
            'sleep_interval_subtitles': random.uniform(1, 3),
            'max_sleep_interval': 10,
        }
        
        # Cloud-optimized bot detection bypass
        is_cloud = os.environ.get('RENDER', False) or os.environ.get('HEROKU', False) or os.environ.get('RAILWAY', False)
        
        if is_cloud:
            # Cloud-specific configuration (no browser cookies)
            print("🌐 Cloud environment detected - using cloud-optimized settings")
            ydl_opts.update({
                'sleep_interval': random.uniform(5, 10),
                'sleep_interval_requests': random.uniform(8, 15),
                'max_sleep_interval': 20,
                'extractor_retries': 15,
                'fragment_retries': 15,
                'retries': 15,
                'file_access_retries': 15,
            })
            # Remove cookie dependency for cloud
            ydl_opts.pop('cookiesfrombrowser', None)
        else:
            # Local development - Chrome cookies are optional
            # Note: Chrome cookies often fail if Chrome is running (database locked)
            # The downloader works fine without them for most videos
            print("🏠 Local environment - Chrome cookies disabled (works without them)")
        
        # Enhanced YouTube API configuration for cloud with advanced bot bypass
        ydl_opts['extractor_args'] = {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_skip': ['configs'],
                'innertube_api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                'innertube_client_version': '2.20231219.01.00',
                'innertube_context': {
                    'client': {
                        'clientName': 'WEB',
                        'clientVersion': '2.20231219.01.00',
                        'originalUrl': 'https://www.youtube.com/',
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                    }
                },
                # Advanced bot detection bypass
                'player_client': 'web',
                'player_skip': ['configs', 'webpage'],
                'comment_sort': 'top',
                'max_comments': [0, 20, 50, 100],
                'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                'context': {
                    'client': {
                        'clientName': 'WEB',
                        'clientVersion': '2.20231219.01.00',
                        'originalUrl': 'https://www.youtube.com/',
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                    }
                }
            }
        }
        
        # Additional bot detection bypass techniques
        ydl_opts.update({
            'writeinfojson': False,
            'writethumbnail': False,
            'writeautomaticsub': False,
            'writesubtitles': False,
            'writeannotations': False,
            'ignoreerrors': True,
            'no_check_certificate': True,
            'prefer_insecure': True,
            'extractor_retries': 10,
            'fragment_retries': 10,
            'retries': 10,
            'file_access_retries': 10,
            'sleep_interval': random.uniform(3, 6),
            'max_sleep_interval': 15,
            'sleep_interval_requests': random.uniform(3, 7),
            'sleep_interval_subtitles': random.uniform(2, 5),
        })

        if format_choice == "MP3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192',}]
        elif format_choice == "720p":
            ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif format_choice == "1080p":
            ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif format_choice == "4K":
            ydl_opts['format'] = 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160]/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif format_choice == "Best Quality":
            ydl_opts['format'] = 'best[ext=mp4]/best'
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            ydl_opts['merge_output_format'] = 'mp4'

        # Platform-specific optimizations
        url_lower = url.lower()
        if 'tiktok.com' in url_lower or 'vm.tiktok.com' in url_lower:
            ydl_opts['extractor_args']['tiktok'] = {'webpage_url_basename': 'video'}
            ydl_opts['format'] = 'best[ext=mp4]/best'
        elif 'instagram.com' in url_lower:
            ydl_opts['extractor_args']['instagram'] = {'include_sidecar': False}
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            ydl_opts['extractor_args']['twitter'] = {'cards': False}
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            ydl_opts['extractor_args']['facebook'] = {'include_dash_manifest': False}
        elif 'twitch.tv' in url_lower:
            ydl_opts['extractor_args']['twitch'] = {'vod_id': True}

        # Multi-step bot detection bypass
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        # Get video info first
                        info = ydl.extract_info(url, download=False)
                        if info:
                            title = info.get('title', 'Unknown')
                            duration = info.get('duration', 0)
                            duration_str = f"{duration // 60}:{duration % 60:02d}" if duration > 0 else "Unknown"
                            download_progress[download_id].update({
                                'status': 'downloading',
                                'message': f"Found: {title[:50]}... ({duration_str})"
                            })
                    except:
                        download_progress[download_id].update({
                            'status': 'downloading',
                            'message': f'Attempt {attempt + 1}: Video info extracted, starting download...'
                        })
                    
                    try:
                        download_progress[download_id].update({
                            'status': 'downloading',
                            'message': f'Attempt {attempt + 1}: Starting download...'
                        })
                    except:
                        pass
                    
                    # Download
                    download_progress[download_id].update({
                        'status': 'downloading',
                        'message': f'Attempt {attempt + 1}: Downloading...'
                    })
                    
                    ydl.download([url])
                    
                    # CRITICAL: Wait for file to be fully written to disk (cloud platforms need this)
                    print(f"⏳ Waiting for file system sync...")
                    time.sleep(2)  # Wait 2 seconds for file to be available
                    
                    break  # Success, exit the retry loop
                    
            except Exception as e:
                error_msg = str(e)
                if "Sign in to confirm you're not a bot" in error_msg or "bot" in error_msg.lower():
                    if attempt < max_attempts - 1:
                        # Wait longer and try different approach
                        wait_time = random.uniform(5, 10) * (attempt + 1)
                        download_progress[download_id].update({
                            'status': 'downloading',
                            'message': f'Bot detected, waiting {int(wait_time)}s before retry {attempt + 2}...'
                        })
                        time.sleep(wait_time)
                        
                        # Modify options for next attempt
                        ydl_opts['sleep_interval'] = random.uniform(5, 10)
                        ydl_opts['sleep_interval_requests'] = random.uniform(5, 10)
                        ydl_opts['http_headers']['User-Agent'] = random.choice(user_agents)
                        continue
                    else:
                        # Final attempt failed
                        raise e
                else:
                    # Different error, don't retry
                    raise e

        # Enhanced file discovery with multiple fallback methods
        downloaded_file = None
        file_path = None
        
        # CRITICAL: Give file system more time to sync (cloud platforms are slower)
        print(f"⏳ Verifying file availability...")
        max_wait = 5  # Wait up to 5 seconds
        wait_increment = 0.5
        waited = 0
        
        # Method 1: Use tracked filename from progress hook (FULL PATH) with retries
        if downloaded_filename:
            print(f"🔍 Looking for tracked file: {downloaded_filename}")
            
            # Retry for up to 5 seconds
            while waited < max_wait:
                if os.path.exists(downloaded_filename) and os.path.isfile(downloaded_filename):
                    file_path = downloaded_filename
                    downloaded_file = os.path.basename(downloaded_filename)
                    file_size = os.path.getsize(file_path)
                    print(f"✅ Method 1: Found tracked file at full path: {file_path}")
                    print(f"✅ Filename: {downloaded_file}, Size: {file_size} bytes")
                    break
                else:
                    print(f"⏳ File not yet available, waiting... ({waited}s/{max_wait}s)")
                    time.sleep(wait_increment)
                    waited += wait_increment
            
            if not downloaded_file:
                print(f"⚠️ Method 1: File still not found after {max_wait}s wait")
                print(f"⚠️ Path checked: {downloaded_filename}")
                print(f"⚠️ File exists: {os.path.exists(downloaded_filename)}")
        
        # Method 2: Search by modification time (fallback)
        if not downloaded_file:
            print(f"🔍 Method 2: Searching downloads directory...")
            print(f"📁 DOWNLOADS_DIR: {DOWNLOADS_DIR}")
            
            try:
                if os.path.exists(DOWNLOADS_DIR):
                    files = os.listdir(DOWNLOADS_DIR)
                    print(f"📋 Total files in directory: {len(files)}")
                    print(f"📋 Files: {files}")
                    
                    downloaded_files = []
                    current_time = time.time()
                    
                    for file in files:
                        temp_path = os.path.join(DOWNLOADS_DIR, file)
                        if os.path.isfile(temp_path):
                            file_mtime = os.path.getmtime(temp_path)
                            file_size = os.path.getsize(temp_path)
                            age_seconds = current_time - file_mtime
                            print(f"   📄 {file}: {file_size} bytes, {age_seconds:.1f}s old")
                            
                            # Check if file was modified in last 10 minutes and has video/audio extension
                            if age_seconds < 600 and file.endswith(('.mp4', '.mp3', '.webm', '.mkv', '.avi', '.mov', '.flv', '.m4a', '.aac', '.ogg', '.wav', '.m4v')):
                                downloaded_files.append((file, file_mtime, temp_path))
                    
                    # Sort by modification time (newest first)
                    downloaded_files.sort(key=lambda x: x[1], reverse=True)
                    
                    if downloaded_files:
                        downloaded_file = downloaded_files[0][0]
                        file_path = downloaded_files[0][2]
                        print(f"✅ Method 2: Found recent file: {downloaded_file}")
                    else:
                        print(f"⚠️ Method 2: No recent video/audio files found")
                else:
                    print(f"❌ Downloads directory does not exist: {DOWNLOADS_DIR}")
            except Exception as e:
                print(f"⚠️ Method 2 failed: {e}")
        
        # Method 3: Direct search for any video/audio file (last resort)
        if not downloaded_file:
            try:
                files = os.listdir(DOWNLOADS_DIR)
                for file in files:
                    if file.endswith(('.mp4', '.mp3', '.webm', '.mkv', '.avi', '.mov', '.flv', '.m4a', '.aac', '.ogg', '.wav', '.m4v')):
                        temp_path = os.path.join(DOWNLOADS_DIR, file)
                        if os.path.isfile(temp_path) and os.path.getsize(temp_path) > 0:
                            downloaded_file = file
                            file_path = temp_path
                            print(f"✅ Method 3: Found any valid file: {downloaded_file}")
                            break
            except Exception as e:
                print(f"⚠️ Method 3 failed: {e}")
        
        # Enhanced debugging for cloud platforms
        if not downloaded_file:
            try:
                all_files = os.listdir(DOWNLOADS_DIR)
                print(f"🔍 DEBUG: No file found. All files in directory: {all_files}")
                print(f"🔍 DEBUG: Downloads directory: {DOWNLOADS_DIR}")
                print(f"🔍 DEBUG: Directory exists: {os.path.exists(DOWNLOADS_DIR)}")
                print(f"🔍 DEBUG: Directory writable: {os.access(DOWNLOADS_DIR, os.W_OK)}")
                print(f"🔍 DEBUG: Tracked filename: {downloaded_filename}")
            except Exception as e:
                print(f"🔍 DEBUG: Error listing directory: {e}")
        
        if downloaded_file:
            # Double-check file exists and get its size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size > 0:
                # Prepare file for immediate download
                download_progress[download_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': f'Download completed! Click to save: {downloaded_file} ({file_size_mb:.2f} MB)',
                    'filename': downloaded_file,
                    'filepath': file_path,
                    'ready_for_download': True  # Signal that file is ready
                })
                
                # Add to history with proper title
                try:
                    # Try to get video title from info if available
                    video_title = info.get('title', downloaded_file) if 'info' in locals() else downloaded_file
                except:
                    video_title = downloaded_file
                    
                history_entry = {
                    'id': download_id,
                    'url': url,
                    'title': video_title,
                    'format': format_choice,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'filename': downloaded_file
                }
                download_history.append(history_entry)
                save_history()
                print(f"✅ Download completed: {downloaded_file} ({file_size_mb:.2f} MB)")
                print(f"📁 File ready at: {file_path}")
            else:
                download_progress[download_id].update({
                    'status': 'error',
                    'message': f'Download completed but file is empty or corrupted: {downloaded_file}',
                    'error': 'File size is 0 bytes'
                })
                print(f"❌ Downloaded file is empty: {downloaded_file}")
        else:
            # If no recent files found, try alternative discovery methods
            print(f"🔍 Debug: No recent files found in {DOWNLOADS_DIR}")
            print(f"🔍 Debug: All files in directory: {files}")
            
            # Try to find any video/audio file
            for file in files:
                if file.endswith(('.mp4', '.mp3', '.webm', '.mkv', '.avi', '.mov', '.flv', '.m4a', '.aac', '.ogg')):
                    downloaded_file = file
                    file_path = os.path.join(DOWNLOADS_DIR, downloaded_file)
                    break
            
            if downloaded_file:
                # Check file size
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                file_size_mb = file_size / (1024 * 1024)
                
                if file_size > 0:
                    download_progress[download_id].update({
                        'status': 'completed',
                        'progress': 100,
                        'message': f'Download completed! File: {downloaded_file} ({file_size_mb:.2f} MB)',
                        'filename': downloaded_file,
                        'filepath': file_path,
                        'ready_for_download': True  # Signal that file is ready
                    })
                    
                    # Add to history
                    history_entry = {
                        'id': download_id,
                        'url': url,
                        'title': downloaded_file,
                        'format': format_choice,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'filename': downloaded_file
                    }
                    download_history.append(history_entry)
                    save_history()
                    print(f"✅ Fallback method: Found {downloaded_file}")
                else:
                    download_progress[download_id].update({
                        'status': 'error',
                        'message': f'Found file but it is empty or corrupted: {downloaded_file}',
                        'error': 'File size is 0 bytes'
                    })
            else:
                # Enhanced error message for cloud deployments
                error_details = {
                    'downloads_dir': DOWNLOADS_DIR,
                    'files_in_dir': files if 'files' in locals() else [],
                    'dir_exists': os.path.exists(DOWNLOADS_DIR),
                    'dir_writable': os.access(DOWNLOADS_DIR, os.W_OK) if os.path.exists(DOWNLOADS_DIR) else False
                }
                print(f"❌ FINAL ERROR: No file found. Details: {error_details}")
                
                download_progress[download_id].update({
                    'status': 'error',
                    'message': f'Download appears to have completed, but the file could not be located. This is a cloud storage timing issue. Please try downloading again.',
                    'error': 'File discovery failed',
                    'debug': error_details
                })

    except Exception as e:
        download_progress[download_id].update({
            'status': 'error',
            'message': f'Download failed: {str(e)}',
            'error': str(e)
        })

@app.route('/')
def index():
    load_history()
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Return empty response for favicon to prevent 404 errors"""
    from flask import make_response
    response = make_response('')
    response.headers['Content-Type'] = 'image/x-icon'
    return response

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    """Return empty response for Chrome DevTools request"""
    return jsonify({})

@app.route('/download', methods=['POST'])
def start_download():
    data = request.get_json()
    url = data.get('url', '').strip()
    format_choice = data.get('format', 'Best Quality')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Generate unique download ID
    download_id = str(uuid.uuid4())
    
    # Start download in background thread
    thread = threading.Thread(target=download_video_task, args=(url, format_choice, download_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({'download_id': download_id})

@app.route('/progress/<download_id>')
def get_progress(download_id):
    if download_id in download_progress:
        return jsonify(download_progress[download_id])
    else:
        return jsonify({'status': 'not_found'}), 404

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        # Security: prevent directory traversal attacks
        filename = os.path.basename(filename)
        
        # Construct absolute path
        file_path = os.path.join(DOWNLOADS_DIR, filename)
        abs_file_path = os.path.abspath(file_path)
        
        # Debug logging for deployment
        print(f"🔍 Download request for: {filename}")
        print(f"📁 Looking in directory: {DOWNLOADS_DIR}")
        print(f"📂 Full path: {abs_file_path}")
        print(f"✅ File exists: {os.path.exists(abs_file_path)}")
        
        # List all files in downloads directory for debugging
        if os.path.exists(DOWNLOADS_DIR):
            all_files = os.listdir(DOWNLOADS_DIR)
            print(f"📋 Files in downloads dir: {all_files}")
        else:
            print(f"❌ Downloads directory doesn't exist: {DOWNLOADS_DIR}")
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            print(f"✅ Created downloads directory")
        
        if os.path.exists(abs_file_path) and os.path.isfile(abs_file_path):
            # Determine MIME type based on extension
            mime_type = 'application/octet-stream'
            if filename.endswith('.mp4'):
                mime_type = 'video/mp4'
            elif filename.endswith('.mp3'):
                mime_type = 'audio/mpeg'
            elif filename.endswith('.webm'):
                mime_type = 'video/webm'
            elif filename.endswith('.mkv'):
                mime_type = 'video/x-matroska'
            
            print(f"✅ Sending file: {filename} ({mime_type})")
            
            # Send file with proper headers for auto-download
            response = send_file(
                abs_file_path,
                as_attachment=True,
                download_name=filename,
                mimetype=mime_type
            )
            
            # Schedule file cleanup after sending (for cloud deployment)
            # This helps manage storage on platforms with limited disk space
            try:
                # Clean up file after 5 minutes to ensure download completes
                def cleanup_file():
                    time.sleep(300)  # Wait 5 minutes
                    try:
                        if os.path.exists(abs_file_path):
                            os.remove(abs_file_path)
                            print(f"🗑️ Cleaned up file: {filename}")
                    except Exception as e:
                        print(f"⚠️ Failed to cleanup file {filename}: {e}")
                
                cleanup_thread = threading.Thread(target=cleanup_file, daemon=True)
                cleanup_thread.start()
            except Exception as e:
                print(f"⚠️ Cleanup thread error: {e}")
            
            return response
        else:
            print(f"❌ File not found: {abs_file_path}")
            return jsonify({
                'error': 'File not found',
                'filename': filename,
                'path': abs_file_path,
                'downloads_dir': DOWNLOADS_DIR,
                'files_available': os.listdir(DOWNLOADS_DIR) if os.path.exists(DOWNLOADS_DIR) else []
            }), 404
    except Exception as e:
        print(f"❌ Error serving file: {str(e)}")
        return jsonify({'error': f'Error serving file: {str(e)}'}), 500

@app.route('/history')
def get_history():
    load_history()
    return jsonify(download_history)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global download_history
    download_history = []
    save_history()
    return jsonify({'message': 'History cleared successfully'})

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """Get video information"""
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        
        # Random user agents to avoid detection (updated with latest versions)
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0'
        ]
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'age_limit': None,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs'],
                    'innertube_api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                    'innertube_client_version': '2.20231219.01.00',
                    'innertube_context': {
                        'client': {
                            'clientName': 'WEB',
                            'clientVersion': '2.20231219.01.00',
                        }
                    }
                }
            },
            'http_headers': {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            },
            # SSL and certificate fixes for cloud deployment
            'nocheckcertificate': True,
            'prefer_insecure': True,
            'legacy_server_connect': True,
            'socket_timeout': 60,
            'connect_timeout': 60,
            'retries': 5,
            'fragment_retries': 5,
            'extractor_retries': 5,
            'sleep_interval': random.uniform(1, 3),
            'sleep_interval_requests': random.uniform(2, 5),
        }
        
        # Cloud-optimized bot detection bypass for video info
        is_cloud = os.environ.get('RENDER', False) or os.environ.get('HEROKU', False) or os.environ.get('RAILWAY', False)
        
        if is_cloud:
            # Cloud-specific configuration (no browser cookies)
            print("🌐 Cloud environment detected - using cloud-optimized settings for video info")
            ydl_opts.update({
                'extractor_retries': 15,
                'fragment_retries': 15,
                'retries': 15,
                'sleep_interval': random.uniform(5, 10),
                'sleep_interval_requests': random.uniform(8, 15),
                'max_sleep_interval': 20,
            })
            # Remove cookie dependency for cloud
            ydl_opts.pop('cookiesfrombrowser', None)
        else:
            # Local development - Chrome cookies disabled (works without them)
            print("🏠 Local environment - Chrome cookies disabled for video info")
            # Enhanced bot detection bypass for video info
            ydl_opts.update({
                'extractor_retries': 10,
                'fragment_retries': 10,
                'retries': 10,
                'sleep_interval': random.uniform(3, 6),
                'sleep_interval_requests': random.uniform(3, 7),
                'max_sleep_interval': 15,
            })
        
        # Multi-attempt approach for video info
        max_attempts = 3
        info = None
        for attempt in range(max_attempts):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    break  # Success
            except Exception as e:
                error_msg = str(e)
                if "Sign in to confirm you're not a bot" in error_msg or "bot" in error_msg.lower():
                    if attempt < max_attempts - 1:
                        # Wait and retry with different settings
                        wait_time = random.uniform(3, 7) * (attempt + 1)
                        time.sleep(wait_time)
                        ydl_opts['sleep_interval'] = random.uniform(5, 10)
                        ydl_opts['http_headers']['User-Agent'] = random.choice(user_agents)
                        continue
                    else:
                        raise e
                else:
                    raise e
        
        if not info:
            raise Exception("Failed to extract video information after multiple attempts")

        formats = []
        if 'formats' in info:
            for fmt in info['formats']:
                if fmt.get('ext') in ['mp4', 'webm', 'mp3'] and (fmt.get('height') or fmt.get('acodec') != 'none'):
                    formats.append({
                        'format_note': fmt.get('format_note') or f"{fmt.get('height')}p" if fmt.get('height') else 'Audio',
                        'ext': fmt.get('ext'),
                        'filesize': fmt.get('filesize', 0)
                    })
        
        # Add common formats if not found
        if not any(f['ext'] == 'mp4' and '1080p' in f['format_note'] for f in formats):
            formats.append({'format_note': '1080p', 'ext': 'mp4', 'filesize': 0})
        if not any(f['ext'] == 'mp4' and '720p' in f['format_note'] for f in formats):
            formats.append({'format_note': '720p', 'ext': 'mp4', 'filesize': 0})
        if not any(f['ext'] == 'mp3' for f in formats):
            formats.append({'format_note': 'MP3', 'ext': 'mp3', 'filesize': 0})

        video_info = {
            'title': info.get('title', 'Unknown Title'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', 'Unknown Uploader'),
            'view_count': info.get('view_count', 0),
            'description': info.get('description', ''),
            'formats': sorted(formats, key=lambda x: x.get('filesize', 0), reverse=True),
            'url': url
        }
        return jsonify(video_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Video Downloader...")
    print("📱 Supports: YouTube, TikTok, Instagram, Twitter/X, Facebook, Twitch & More")
    print("🎯 Features: Age restriction bypass, multiple qualities, real-time progress")
    
    # Display speed optimization status
    if ARIA2C_AVAILABLE:
        print("⚡ Speed Boost: aria2c detected - Ultra-fast downloads enabled (16 connections)")
    else:
        print("⚡ Speed Boost: Multi-threaded downloads enabled (16 concurrent fragments)")
        print("💡 Tip: Install aria2c for even faster downloads (up to 10x speed)")
    
    # Production-ready configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"\n🌐 Server starting at: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
