# 🔍 SEO Crawler Pro - Streamlit Edition

An advanced web scraping and NLP analysis tool for extracting key entities from websites using Google Cloud Natural Language API.

## 🌟 Features

- **🕷️ Web Crawling**: Intelligent site-wide crawling with configurable depth
- **🧠 NLP Analysis**: Google Cloud Natural Language entity extraction
- **📊 CSV Export**: Download results for further analysis
- **⚡ Real-time Progress**: Live updates during analysis
- **🎨 Modern UI**: Clean, intuitive Streamlit interface
- **⚙️ Configurable**: Adjust crawl depth, max pages, timeouts
- **🔒 Secure**: Credentials handled securely via file upload or Streamlit secrets

## 🚀 Quick Start

### Local Installation

```bash
# Clone or navigate to project directory
cd /Users/aslan/Documents/AIO\ NLP

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

Open browser to `http://localhost:8501`

### Get Google Credentials

1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create a project and enable **Cloud Natural Language API**
3. Create a Service Account and download JSON key
4. Upload via app interface or add to Streamlit secrets

## 📖 How to Use

### 1. Load Credentials
- Click "📁 Upload JSON Key" in sidebar
- Select your Google Cloud service account JSON file
- Confirm "✓ [filename] loaded"

### 2. Configure Settings
- **Max Pages**: How many pages to crawl (1-50)
- **Crawl Depth**: How many link levels to follow (1-3)
- Or use Quick Presets: 🏃 Quick (3 pages) or ⚙️ Normal (10 pages)

### 3. Enter Website
- Paste target URL (e.g., `https://www.example.com`)
- Click "▶ LAUNCH ANALYSIS"

### 4. Review Results
- Watch real-time progress log
- Download CSV when complete
- View results in interactive table

## 📊 Output Format

CSV includes:
- **source**: Page URL
- **name**: Entity name
- **salience**: Importance (0-1 scale)
- **category**: Entity type (PERSON, ORG, LOCATION, etc.)

## 🔧 Configuration

### Streamlit Settings (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#1f6aa5"
backgroundColor = "#ffffff"

[client]
showErrorDetails = true
```

### Environment Variables
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## 🛠️ Advanced Usage

### CLI Mode (Original)
```bash
python analyze2.py --url https://example.com \
                   --creds credentials.json \
                   --pages 10 \
                   --depth 2 \
                   --out results.csv
```

### Python API
```python
from streamlit_app import SEOLogic

# Crawl a site
urls = SEOLogic.crawl("https://example.com", max_pages=5, max_depth=2)

# Analyze text
text = SEOLogic.fetch_content("https://example.com")
entities = SEOLogic.analyze_entities(text, "https://example.com")
```

## 📈 Performance & Costs

- **Crawling**: ~1-2 seconds per page
- **Analysis**: ~2-5 seconds per page (depends on text length)
- **Google Cloud**: ~$1 per 1,000 requests (entity extraction)
- **Tip**: Test with Quick preset first

## ⚠️ Important Notes

1. **Respect robots.txt** - Don't crawl too aggressively
2. **Monitor API costs** - Check Google Cloud billing regularly
3. **Security**: Never commit credentials to GitHub
4. **Timeouts**: Some websites may block scrapers

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No credentials loaded" | Upload JSON file in sidebar or set env var |
| "ImportError: google-cloud-language" | Run: `pip install google-cloud-language` |
| Analysis is very slow | Reduce max pages or crawl depth |
| No entities found | Website may be JavaScript-only; try another site |
| "Timeout" errors | Website blocking requests; check User-Agent headers |

## 📚 Documentation

- [Full Deployment Guide](STREAMLIT_DEPLOY.md)
- [Google Cloud NLP Docs](https://cloud.google.com/natural-language/docs)
- [Streamlit Documentation](https://docs.streamlit.io)

## 🏗️ Architecture

```
streamlit_app.py
├── SEOLogic (Core Logic)
│   ├── normalize_url()
│   ├── fetch_content()
│   ├── analyze_entities()
│   └── crawl()
├── Streamlit UI
│   ├── Sidebar (Config)
│   ├── Main Area (Analysis)
│   └── Tabs (Analysis, Help, Settings)
└── File Management
    └── CSV Export
```

## 🔐 Security

- Credentials stored locally only (`.seo_crawler/config.json`)
- File upload supports file size up to 200MB
- No data sent to external servers except Google Cloud API
- HTTPS recommended for cloud deployment

## 📦 Dependencies

```
streamlit==1.28.1
requests==2.31.0
beautifulsoup4==4.12.2
google-cloud-language==2.11.1
google-auth==2.25.2
```

## 🌐 Deployment Options

### Local
```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud
- Push to GitHub
- Connect at https://streamlit.io/cloud
- Add secrets via dashboard

### Docker
```bash
docker build -t seo-crawler .
docker run -p 8501:8501 seo-crawler
```

### AWS/Heroku/DigitalOcean
- Standard Streamlit deployment
- Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## 📝 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Improvements welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📞 Support

For issues:
1. Check [Troubleshooting](#troubleshooting)
2. Review [Full Guide](STREAMLIT_DEPLOY.md)
3. Check Google Cloud Console for API errors
4. Verify credentials and permissions

---

**Last Updated**: January 30, 2026
**Status**: ✅ Production Ready
