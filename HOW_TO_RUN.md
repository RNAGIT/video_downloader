# How to Run Video Downloader Project

## 🚀 Quick Start Guide

### **Step 1: Install Python**
1. Download Python from [python.org](https://python.org)
2. Install Python 3.8 or higher
3. Make sure to check "Add Python to PATH" during installation

### **Step 2: Open Command Prompt/Terminal**
- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **Mac**: Press `Cmd + Space`, type `Terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

### **Step 3: Navigate to Project Folder**
```bash
cd C:\Users\USER\Desktop\Projects\youtube_video_downloader
```

### **Step 4: Install Required Packages**
```bash
pip install -r requirements.txt
```

### **Step 5: Run the Application**
```bash
python app.py
```

### **Step 6: Open Your Browser**
1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Go to: `http://localhost:5000`
3. You should see the video downloader interface!

---

## 📋 Detailed Instructions

### **1. Check Python Installation**
```bash
python --version
```
Should show: `Python 3.8.x` or higher

### **2. Install Dependencies**
```bash
pip install Flask==2.3.3
pip install yt-dlp==2023.12.30
pip install requests==2.31.0
pip install aiohttp==3.9.1
pip install tqdm==4.66.1
```

### **3. Verify Installation**
```bash
python -c "import flask, yt_dlp; print('✅ All packages installed successfully!')"
```

### **4. Run the Application**
```bash
python app.py
```

### **5. Expected Output**
```
🚀 Starting Simple Video Downloader...
📱 Supports: YouTube, TikTok, Instagram, Twitter/X, Facebook, Twitch & More
🎯 Features: Age restriction bypass, multiple qualities, real-time progress

🌐 Server starting at: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

---

## 🌐 How to Use the Web Interface

### **1. Access the Website**
- Open browser and go to: `http://localhost:5000`
- You'll see a beautiful video downloader interface

### **2. Download a Video**
1. **Paste video URL** in the input field
2. **Select quality** (Best Quality, 1080p, 720p, MP3, etc.)
3. **Click "Start Download"**
4. **Watch progress** in real-time
5. **Download file** when complete

### **3. Supported Platforms**
- ✅ YouTube
- ✅ TikTok
- ✅ Instagram
- ✅ Twitter/X
- ✅ Facebook
- ✅ Twitch
- ✅ Vimeo
- ✅ And 1000+ more!

---

## 🔧 Troubleshooting

### **Problem: "Python not found"**
**Solution:**
```bash
# Try python3 instead
python3 app_optimized.py

# Or check if Python is in PATH
where python
```

### **Problem: "Module not found"**
**Solution:**
```bash
# Install missing packages
pip install Flask yt-dlp requests

# Or install all at once
pip install -r requirements.txt
```

### **Problem: "Port 5000 already in use"**
**Solution:**
```bash
# Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

### **Problem: "Permission denied"**
**Solution:**
```bash
# Run as administrator (Windows)
# Or use sudo (Mac/Linux)
sudo python app_optimized.py
```

### **Problem: "Download failed"**
**Solution:**
1. Check internet connection
2. Verify video URL is correct
3. Try different quality setting
4. Check if video is private/age-restricted

---

## 📱 Mobile Access

### **Access from Mobile Device**
1. Find your computer's IP address:
   ```bash
   # Windows:
   ipconfig
   
   # Mac/Linux:
   ifconfig
   ```

2. On your mobile device, go to:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```
   Example: `http://192.168.1.100:5000`

3. Use the mobile-friendly interface!

---

## ⚡ Performance Tips

### **For Best Performance:**
1. **Use optimized version**: `python app_optimized.py`
2. **Close other programs** using internet
3. **Use wired connection** instead of WiFi
4. **Clear cache** if downloads are slow

### **Speed Optimizations Active:**
- 🚀 **Multi-threaded downloads** (12 workers)
- ⚡ **Concurrent fragments** (16 simultaneous)
- 💾 **Smart caching** system
- 🔄 **Connection pooling**
- 🎯 **Platform-specific optimizations**

---

## 📁 Project Structure

```
youtube_video_downloader/
├── app.py                  # Main Flask server
├── templates/
│   └── index.html         # Web interface
├── downloads/             # Downloaded videos (auto-created)
├── requirements.txt       # Python dependencies (Flask + yt-dlp only)
├── HOW_TO_RUN.md         # This file
└── README_WEB.md         # Documentation
```

---

## 🎯 Quick Commands

### **Start Server:**
```bash
python app.py
```

### **Install Dependencies:**
```bash
pip install -r requirements.txt
```

### **Check Python Version:**
```bash
python --version
```

### **Clear Cache:**
```bash
# Delete cache folder
rmdir /s video_cache

# Or use the web interface cache clear button
```

---

## 🌟 Features You'll Get

### **🎥 Video Downloading:**
- Download from 1000+ platforms
- Multiple quality options (4K, 1080p, 720p, MP3)
- Age restriction bypass
- Real-time progress tracking

### **⚡ Speed Features:**
- Multi-threaded downloads
- Concurrent fragment downloads
- Smart caching system
- Connection pooling

### **🎨 User Interface:**
- Beautiful, responsive design
- Dark/light theme toggle
- Mobile-friendly
- Real-time progress bars

### **🔧 Advanced Features:**
- Download history
- Platform-specific optimizations
- Error handling and retries
- Cache management

---

## 🆘 Need Help?

### **Common Issues:**
1. **Python not installed** → Download from python.org
2. **Packages not found** → Run `pip install -r requirements.txt`
3. **Port in use** → Kill process using port 5000
4. **Download fails** → Check URL and internet connection

### **Success Indicators:**
- ✅ Server starts without errors
- ✅ Browser shows video downloader interface
- ✅ Can paste URLs and see video info
- ✅ Downloads complete successfully

---

## 🎉 You're Ready!

Once you see the message:
```
🌐 Server starting at: http://localhost:5000
```

You're all set! Open your browser and start downloading videos! 🚀

**Happy Downloading!** 🎥✨
