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

        # Prepare yt-dlp options with age restriction bypass and SSL fixes
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
                }
            },
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'sleep_interval_subtitles': 1,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retries': 3,
            'no_color': True,
            'quiet': True,
            'no_warnings': True,
            # SSL and certificate fixes for cloud deployment
            'nocheckcertificate': True,
            'prefer_insecure': True,
            'legacy_server_connect': True,
            'source_address': '0.0.0.0',
            'socket_timeout': 30,
            'connect_timeout': 30,
            'http_chunk_size': 10485760,  # 10MB chunks
            'fragment_retries': 5,
            'retry_sleep_functions': {'http': lambda n: min(4 ** n, 60)},
        }

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
                    'message': 'Video info extracted, starting download...'
                })
            
            try:
                download_progress[download_id].update({
                    'status': 'downloading',
                    'message': 'Starting download...'
                })
            except:
                pass
            
            # Download
            download_progress[download_id].update({
                'status': 'downloading',
                'message': 'Starting download...'
            })
            
            ydl.download([url])

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
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'age_limit': None,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            # SSL and certificate fixes for cloud deployment
            'nocheckcertificate': True,
            'prefer_insecure': True,
            'legacy_server_connect': True,
            'socket_timeout': 30,
            'connect_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

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
