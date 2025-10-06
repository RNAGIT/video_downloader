<<<<<<< HEAD
# 🎥 Universal Social Media Video Downloader

A powerful web-based video downloader that supports 1000+ social media platforms with age restriction bypass and beautiful responsive interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

- **🌍 Universal Support**: YouTube, TikTok, Instagram, Twitter/X, Facebook, Twitch, Vimeo & more
- **🔓 Age Restriction Bypass**: Automatically bypasses age restrictions
- **🎯 Multiple Quality Options**: 4K, 1080p, 720p, MP4, MP3
- **📊 Real-time Progress**: Live download progress tracking
- **📱 Mobile Responsive**: Works perfectly on all devices
- **🎨 Beautiful UI**: Modern design with dark/light theme toggle
- **📁 Download History**: Track and re-download previous videos
- **⚡ Fast Downloads**: Optimized for speed and efficiency

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/youtube_video_downloader.git
   cd youtube_video_downloader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Go to: `http://localhost:5000`

## 📱 How to Use

1. **Paste any video URL** from supported platforms
2. **Select your preferred quality** (Best Quality, 1080p, 720p, MP3, etc.)
3. **Click "Start Download"**
4. **Watch the real-time progress**
5. **Download your file when complete**

## 🌐 Supported Platforms

- ✅ **YouTube** (including age-restricted content)
- ✅ **TikTok** (with watermark removal)
- ✅ **Instagram** (posts, stories, reels)
- ✅ **Twitter/X** (video tweets)
- ✅ **Facebook** (watch videos)
- ✅ **Twitch** (clips, VODs)
- ✅ **Vimeo**
- ✅ **And 1000+ more platforms**

## 🛠️ Technical Details

### Built With
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Video Processing**: yt-dlp with enhanced bypass options
- **Real-time Updates**: AJAX polling for progress
- **File Management**: Automatic download organization

### Project Structure
```
youtube_video_downloader/
├── app.py                  # Main Flask server
├── templates/
│   └── index.html         # Web interface
├── downloads/             # Downloaded videos (auto-created)
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚀 Deployment Options

### Option 1: Heroku (Free)
1. Create account at [Heroku](https://heroku.com)
2. Install Heroku CLI
3. Create `Procfile`:
   ```
   web: python app.py
   ```
4. Deploy:
   ```bash
   git add .
   git commit -m "Initial commit"
   heroku create your-app-name
   git push heroku main
   ```

### Option 2: Railway (Free)
1. Create account at [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables if needed
4. Deploy automatically

### Option 3: Render (Free)
1. Create account at [Render](https://render.com)
2. Connect your GitHub repository
3. Select "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`

### Option 4: VPS/Cloud Server
1. Set up Ubuntu/CentOS server
2. Install Python and dependencies
3. Use PM2 or systemd for process management
4. Set up reverse proxy with Nginx

## 📋 Environment Variables

Create a `.env` file for production:
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
PORT=5000
```

## 🔧 Configuration

### Customize Download Settings
Edit `app.py` to modify:
- Default download quality
- Download folder location
- Maximum file size
- Platform-specific settings

### UI Customization
Edit `templates/index.html` to:
- Change colors and themes
- Add new features
- Modify layout
- Update branding

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please respect copyright laws and the terms of service of each platform. Only download videos you have permission to download.

## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/yourusername/youtube_video_downloader/issues) page
2. Create a new issue with detailed information
3. Check the troubleshooting section in [HOW_TO_RUN.md](HOW_TO_RUN.md)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/youtube_video_downloader&type=Date)](https://star-history.com/#yourusername/youtube_video_downloader&Date)

---

**Made with ❤️ for the community**

⭐ **Star this repository if you find it helpful!**
=======
# video_downloader
>>>>>>> a69e9bb4cc3abea2e0bae1cbffc1327df7f59165
