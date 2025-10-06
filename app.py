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
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Global storage for download progress
download_progress = {}
download_history = []

# Create downloads directory
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

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
        
        # Progress hook
        def progress_hook(d):
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
                download_progress[download_id].update({
                    'status': 'finished',
                    'progress': 100,
                    'message': 'Download complete!'
                })

        # Prepare yt-dlp options with bot detection bypass and SSL fixes
        import random
        import time
        
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
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'postprocessors': [],
            'geo_bypass': True,
            'nocheckcertificate': True,
            'restrictfilenames': True,
            'noplaylist': True,
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
            # Additional cloud-optimized settings
            'sleep_interval_requests': random.uniform(2, 5),
            'sleep_interval_subtitles': random.uniform(1, 3),
            'max_sleep_interval': 10,
        }
        
        # Cloud-optimized bot detection bypass
        import os
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
            # Local development - try to use Chrome cookies
            try:
                ydl_opts['cookiesfrombrowser'] = ('chrome',)
                print("🏠 Local environment - using Chrome cookies")
            except:
                print("🏠 Local environment - Chrome cookies not available")
                pass
        
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

        # Find downloaded file
        files = os.listdir(DOWNLOADS_DIR)
        downloaded_file = None
        for file in files:
            if file.endswith(('.mp4', '.mp3', '.webm', '.mkv')):
                downloaded_file = file
                break

        if downloaded_file:
            download_progress[download_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Download completed successfully!',
                'filename': downloaded_file,
                'filepath': os.path.join(DOWNLOADS_DIR, downloaded_file)
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
        else:
            download_progress[download_id].update({
                'status': 'error',
                'message': 'Download completed but file not found'
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
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

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
        import random
        
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
        import os
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
            # Local development - try to use Chrome cookies
            try:
                ydl_opts['cookiesfrombrowser'] = ('chrome',)
                print("🏠 Local environment - using Chrome cookies for video info")
            except:
                print("🏠 Local environment - Chrome cookies not available for video info")
                pass
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
    
    # Production-ready configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"\n🌐 Server starting at: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
