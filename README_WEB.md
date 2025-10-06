# Universal Social Media Video Downloader - Web Version

A powerful web-based video downloader that supports 1000+ social media platforms with age restriction bypass.

## 🌟 Features

- **Universal Support**: YouTube, TikTok, Instagram, Twitter/X, Facebook, Twitch, Vimeo & more
- **Age Restriction Bypass**: Automatically bypasses age restrictions
- **Multiple Quality Options**: 4K, 1080p, 720p, MP4, MP3
- **Real-time Progress**: Live download progress tracking
- **Download History**: Track and re-download previous videos
- **Modern Web Interface**: Beautiful, responsive design
- **Cross-platform**: Works on any device with a web browser

### 🚀 **Speed Optimizations**

- **Multi-threaded Downloads**: 12 concurrent workers for maximum speed
- **Concurrent Fragment Downloads**: 16 simultaneous fragment downloads
- **Chunked Transfers**: 16KB chunks for faster data transfer
- **Connection Pooling**: 100 concurrent connections
- **Smart Caching**: Intelligent download caching system
- **Platform-specific Optimizations**: Auto-optimized settings for each platform
- **Retry Mechanism**: 3 automatic retries with backoff
- **HTTP/2 Support**: Modern protocol for faster transfers

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Optimized Web Application
```bash
# For maximum speed (recommended)
python app_optimized.py

# Or use the standard version
python app.py
```

### 3. Open Your Browser
Go to: `http://localhost:5000`

## 📱 Supported Platforms

- **YouTube** (including age-restricted content)
- **TikTok**
- **Instagram** (posts, stories, reels)
- **Twitter/X** (video tweets)
- **Facebook** (watch videos)
- **Twitch** (clips, VODs)
- **Vimeo**
- **And 1000+ more platforms**

## 🎯 How to Use

1. **Open the web app** in your browser
2. **Paste any video URL** from supported platforms
3. **Select quality** (Best Quality recommended)
4. **Click "Start Download"**
5. **Wait for completion** and download your file

## 🔧 Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Video Processing**: yt-dlp with enhanced bypass options
- **Real-time Updates**: AJAX polling for progress
- **File Management**: Automatic download organization

## 🛡️ Age Restriction Bypass

The application automatically:
- Bypasses age restrictions on YouTube and other platforms
- Uses user agent rotation to avoid detection
- Implements multiple retry mechanisms
- Handles region-blocked content

## 📁 File Structure

```
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── downloads/            # Downloaded files (auto-created)
├── download_history.json # Download history
├── requirements.txt      # Python dependencies
└── README_WEB.md        # This file
```

## 🌐 Deployment

### Local Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## ⚠️ Important Notes

- **Legal Compliance**: Only download videos you have permission to download
- **Platform Terms**: Respect each platform's terms of service
- **Educational Purpose**: This tool is for educational purposes
- **Copyright**: Respect copyright laws and content creators' rights

## 🔄 Updates

To update yt-dlp for better compatibility:
```bash
pip install --upgrade yt-dlp
```

## 🐛 Troubleshooting

### Common Issues:

1. **"Download failed"**: 
   - Check internet connection
   - Verify URL is valid and public
   - Try different quality settings

2. **"Age-restricted content"**:
   - The app automatically bypasses age restrictions
   - If still failing, try updating yt-dlp

3. **"File not found"**:
   - Check if video is private or deleted
   - Try a different video URL

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Update yt-dlp: `pip install --upgrade yt-dlp`
3. Verify the video URL is public and accessible

---

**Enjoy downloading videos from any social media platform! 🎉**
