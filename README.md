# 🔍 SEO Crawler Pro - User-Friendly Edition

## ✨ New Features & Improvements

### 🎨 Enhanced User Interface
- **Modern Design**: Cleaner, more intuitive layout with emoji icons
- **Multi-Tab Interface**: Organized sections for Log, Help, and Settings
- **Recent URLs History**: Quick access to sites you've analyzed before
- **Quick Presets**: One-click "Quick (3 pages)" and "Normal (10 pages)" analysis modes
- **Progress Feedback**: Real-time progress updates and visual indicators

### 💾 Smart Settings
- **Auto-Save Configuration**: Your preferences are remembered (credentials, max pages, depth)
- **Persistent History**: Last 10 URLs you analyzed are saved
- **Config Location**: `~/.seo_crawler/config.json`

### 🚀 Everyday Use Features
- **Keyboard Shortcut**: Press `Enter` in URL field to start analysis
- **Auto-URL Format**: Automatically adds `https://` if missing
- **Better Error Messages**: Clear, actionable error notifications
- **Helpful Tooltips**: In-app help button for Google Cloud setup
- **Smart Filenames**: Suggests output CSV name based on website

### 📊 Icon & Branding
- **Built-in Icon**: Custom SEO icon (no external files needed)
- **Professional Title**: "SEO Crawler Pro - Easy Everyday Analyzer"

---

## 🚀 Quick Start

### Option 1: GUI (Recommended)
```bash
cd "/Users/aslan/Documents/AIO NLP"
python3 analyze2.py
```

### Option 2: Desktop Launcher (Easiest)
Double-click `launch.sh` or:
```bash
bash launch.sh
```

### Option 3: CLI (Advanced)
```bash
python3 analyze2.py --url https://example.com --creds /path/to/key.json --pages 10 --depth 2 --out report.csv
```

---

## 📋 Setup Instructions

### Step 1️⃣: Get Google Cloud Credentials
1. Visit: https://console.cloud.google.com
2. Create a new project
3. Search for "Natural Language API" → Enable it
4. Go to **Credentials** → **Create Service Account**
5. Download the JSON key
6. Keep it safe!

### Step 2️⃣: Load Credentials in App
1. Click **📁 Load JSON Key** button
2. Select your downloaded JSON file
3. You'll see ✓ confirmation

### Step 3️⃣: Analyze Websites
1. Enter website URL (e.g., `https://www.bbc.com`)
2. Choose preset (Quick = fast, Normal = thorough)
3. Click **▶ LAUNCH ANALYSIS**
4. Download CSV when done!

---

## 💡 Pro Tips

| Tip | Details |
|-----|---------|
| **🏃 Quick Mode** | Analyze 3 pages in ~1-2 min for testing |
| **⚙️ Normal Mode** | Analyze 10 pages with depth 2 (best balance) |
| **📌 Recent URLs** | Click any recent URL to reload it instantly |
| **🔄 Auto-Save** | Settings persist between sessions |
| **📊 CSV Output** | Open in Excel/Google Sheets for analysis |

---

## 📊 What Gets Analyzed?

Each website crawl produces a CSV with:
- **Source**: The page URL
- **Name**: Entity detected (person, place, organization, etc.)
- **Salience**: Importance score (0-1)
- **Category**: Entity type (PERSON, LOCATION, EVENT, etc.)

Example output:
```
source,name,salience,category
https://www.bbc.com/news,London,0.85,LOCATION
https://www.bbc.com/news,BBC,0.92,ORGANIZATION
https://www.bbc.com/sport,World Cup,0.78,EVENT
```

---

## ⚙️ Configuration

Settings are auto-saved to: `~/.seo_crawler/config.json`

```json
{
  "max_pages": 10,
  "max_depth": 2,
  "creds_path": "/path/to/credentials.json",
  "recent_urls": ["https://example.com", ...]
}
```

### Reset Settings
Delete `~/.seo_crawler/` and restart the app:
```bash
rm -rf ~/.seo_crawler/
```

---

## 🆘 Troubleshooting

### ❌ "No key loaded" error
→ Click **ℹ️** button next to credentials to get setup help

### ❌ "Could not fetch content"
→ Website might be blocking bots. Try a different site.

### ❌ macOS "abort" error
→ System Tk incompatibility. Use `launch.sh` script instead.

### ❌ "No entities found"
→ Page might be JavaScript-heavy or minimal text. Try homepage instead.

---

## 📦 Dependencies

Automatically installed with setup:
- `customtkinter` - Modern GUI framework
- `beautifulsoup4` - Web scraping
- `requests` - HTTP client
- `google-cloud-language` - NLP analysis
- `python3.9+`

Install missing packages:
```bash
pip install customtkinter beautifulsoup4 requests google-cloud-language
```

---

## 📈 Typical Workflow

```
1. App loads → Check "Recent URLs" tab
2. Enter new URL or click recent one
3. Click "Quick" preset (3 pages, ~2 min)
4. Watch the progress bar
5. Download CSV from Desktop
6. Open in Excel/Sheets
7. Sort by "Salience" to find key entities
8. Next analysis → auto-saved settings!
```

---

## 🎯 Use Cases

| Use Case | Recommended Settings |
|----------|----------------------|
| **Quick Testing** | Quick preset (3 pages, depth 1) |
| **Full Audit** | Normal preset (10 pages, depth 2) |
| **Deep Dive** | 20+ pages, depth 3 (takes 5+ min) |
| **Small Blog** | 5 pages, depth 1 |
| **News Site** | 15 pages, depth 2 |

---

## 🔐 Security & Privacy

- **Credentials**: Only sent to Google Cloud (never stored locally in plain text)
- **Local Storage**: Config saved in `~/.seo_crawler/` only
- **History**: Recent URLs stored locally for convenience
- **Websites**: Standard HTTP headers only (no cookies stored)

---

## 📞 Support

### Common Questions

**Q: Why is analysis slow?**
A: Large sites with depth 3 take 5-10 minutes. Use "Quick" preset for testing.

**Q: Can I analyze local websites?**
A: No, only public websites. Localhost won't work.

**Q: Can I re-analyze the same site?**
A: Yes! Click the URL from Recent URLs or paste it again.

**Q: How much does Google NLP cost?**
A: First 5,000 requests/month free. Then $1/1000 requests.

---

## 🚀 Launching from Desktop (One-Click)

### macOS: Create Desktop Shortcut
```bash
# Create launcher on Desktop
cat > ~/Desktop/SEO\ Crawler.command << 'EOF'
#!/bin/bash
cd "/Users/aslan/Documents/AIO NLP"
/usr/bin/python3 analyze2.py
EOF
chmod +x ~/Desktop/SEO\ Crawler.command
```

Then just **double-click** `SEO Crawler.command` on Desktop!

---

**Version**: 2.0 (Pro Edition)  
**Last Updated**: 2026-01-22  
**Tested on**: macOS 15+, Python 3.9+
