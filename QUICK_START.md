# 🚀 Quick Reference Guide

## Launching SEO Crawler

### Easiest Method (Recommended)
```bash
bash "launch.sh"
```
Or double-click `launch.sh` in Finder

### Command Line
```bash
cd "/Users/aslan/Documents/AIO NLP"
python3 analyze2.py
```

### Create One-Click Desktop Launcher
Run once:
```bash
bash create_app_bundle.sh
```
Then find "SEO Crawler Pro" in Applications (or Spotlight search)

---

## 5-Minute Setup

1. **Get Google Credentials** (5 min)
   - Go to console.cloud.google.com
   - Create project → Enable Natural Language API
   - Create Service Account → Download JSON
   
2. **Launch App**
   ```bash
   python3 analyze2.py
   ```

3. **Load Credentials**
   - Click 📁 Load JSON Key
   - Select your downloaded file
   - See ✓ confirmation

4. **Analyze Website**
   - Enter URL: `https://www.example.com`
   - Click Quick preset (fastest)
   - Click ▶ LAUNCH ANALYSIS
   - Wait 2-3 minutes
   - Download CSV

5. **View Results**
   - Open CSV in Excel
   - Sort by "Salience" (importance)
   - See: URLs, Entities, Importance Scores, Types

---

## All Features at a Glance

| Feature | Benefit |
|---------|---------|
| 💾 **Auto-Save Settings** | Remembers credentials & preferences |
| 📌 **Recent URLs History** | Quick re-analysis with one click |
| 🏃 **Quick Presets** | 3-page test or 10-page full audit |
| 🎨 **Modern Interface** | Emoji icons, tabs, organized layout |
| 🔄 **Persistent Config** | Settings survive app restart |
| ⌨️ **Enter to Launch** | Just press Enter in URL field |
| 🆘 **Built-in Help** | ℹ️ buttons explain everything |
| 📊 **Detailed Progress** | See exactly what's being analyzed |

---

## Common Tasks

### 💨 Quick 2-Minute Test
```
1. URL: https://example.com
2. Click "Quick" preset
3. Click ▶ LAUNCH
4. Download CSV when done
```

### 📋 Full Site Audit (5-10 minutes)
```
1. URL: https://example.com
2. Click "Normal" preset
3. Modify pages/depth if needed
4. Click ▶ LAUNCH
5. Download and analyze results
```

### 🔄 Re-analyze Same Site
```
1. Click recent URL in sidebar
2. URL auto-fills
3. Click ▶ LAUNCH
4. Download CSV
```

### 📁 Find Your Results
```
Location: ~/Downloads/ (or your chosen folder)
Format: seo_audit_[website].csv
Open in: Excel, Google Sheets, or Calc
```

---

## Settings & Config

All preferences stored in:
```
~/.seo_crawler/config.json
```

Includes:
- ✓ Credentials path
- ✓ Last used settings (max pages, depth)
- ✓ Recent URL history (10 most recent)

To reset: Delete `~/.seo_crawler/` folder

---

## Pro Tips

🔥 **Hot Tips for Best Results:**

1. **Test First** - Use "Quick" preset (3 pages) before large audits
2. **Homepage First** - Analyze homepage, then deep pages
3. **Sort Results** - Open CSV, sort by "Salience" for top entities
4. **Check Category** - Look for ORGANIZATION, PERSON, LOCATION
5. **Reuse History** - Click Recent URLs to quickly re-analyze sites
6. **Batch Analysis** - Analyze competitor sites back-to-back
7. **Keep CSVs** - Archive old reports for comparison
8. **Check Logs** - Scroll analysis log for details

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| ❌ "No key loaded" | Click ℹ️ button, follow Google Cloud setup |
| ❌ App won't start | Try: `python3 analyze2.py` in Terminal |
| ❌ Slow analysis | Use "Quick" preset instead of "Normal" |
| ❌ No entities found | Try different URL or homepage instead |
| ❌ CSV won't open | Make sure you picked a valid save location |
| ❌ macOS "abort" | Use `launch.sh` instead of direct run |

---

## Files Included

```
analyze2.py           ← Main application (run this!)
launch.sh             ← Easy launcher script
README.md             ← Full documentation
QUICK_START.md        ← This file
generate_icon.py      ← Icon generator (optional)
create_app_bundle.sh  ← macOS app creator (optional)
```

---

## Performance Expectations

| Settings | Time | Pages | Coverage |
|----------|------|-------|----------|
| Quick (3, depth 1) | 2 min | 3 | Homepage + 2 linked |
| Normal (10, depth 2) | 5-8 min | 10 | Good site coverage |
| Deep (20, depth 3) | 15+ min | 20+ | Comprehensive audit |
| Large Sites (50, depth 2) | 20+ min | 50+ | Full inventory |

---

## Next Steps

1. ✅ Install dependencies if needed:
   ```bash
   pip install customtkinter beautifulsoup4 requests google-cloud-language
   ```

2. ✅ Get Google Cloud credentials (free tier available)

3. ✅ Launch the app:
   ```bash
   python3 analyze2.py
   ```

4. ✅ Analyze your first website!

---

**Version:** 2.0  
**Status:** ✅ Production Ready  
**Python:** 3.9+  
**Platform:** macOS 10.14+, Linux, Windows
