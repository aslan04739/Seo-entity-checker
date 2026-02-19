# 🚀 Streamlit Deployment Guide - SEO Crawler Pro

## ✅ Local Testing (Quick Start)

### 1️⃣ Install dependencies
```bash
cd /Users/aslan/Documents/AIO\ NLP
pip install -r requirements.txt
```

### 2️⃣ Run locally
```bash
streamlit run streamlit_app.py
```

The app will be available at **`http://localhost:8501`**

### 3️⃣ Test the interface
- Upload a Google Cloud JSON credentials file
- Enter a website URL (e.g., `https://example.com`)
- Adjust Max Pages (1-50) and Crawl Depth (1-3)
- Click "LAUNCH ANALYSIS"
- Download results as CSV

---

## 🌐 Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- Google Cloud credentials JSON file
- Project pushed to GitHub repository

### Step-by-Step Deployment

#### 1. Prepare GitHub Repository
```bash
# Create a new repo with these files:
# - streamlit_app.py
# - requirements.txt
# - .streamlit/config.toml
# - README.md

git add .
git commit -m "Initial Streamlit deployment"
git push origin main
```

#### 2. Deploy on Streamlit Cloud
1. Visit **https://streamlit.io/cloud**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository
5. Select `streamlit_app.py` as the main file
6. Click **"Deploy"**

#### 3. Configure Secrets (Google Credentials)
1. Go to app Settings → **Secrets**
2. Add your Google Cloud JSON credentials:
   ```toml
   [google]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "your-email@project.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your-cert-url"
   ```
3. Click **"Save"**

#### 4. Your App is Live! 🎉
- URL: `https://[username]-[appname].streamlit.app`
- Share with anyone
- Auto-updates on GitHub push

---

## 🔑 Get Google Cloud Credentials

### 1. Create Google Cloud Project
1. Visit **https://console.cloud.google.com**
2. Click **"Create Project"**
3. Enter project name: `SEO Crawler`
4. Click **"Create"**

### 2. Enable Natural Language API
1. Search for **"Cloud Natural Language API"**
2. Click the API
3. Click **"Enable"**

### 3. Create Service Account
1. Go to **IAM & Admin → Service Accounts**
2. Click **"Create Service Account"**
3. Name: `seo-crawler-bot`
4. Click **"Create"**
5. Grant role: **"Viewer"** (read-only)
6. Click **"Continue"**
7. Click **"Create Key"** → **JSON**
8. Download the file
9. Keep it safe! ⚠️

### 4. Upload to Streamlit
- **Local**: Use "Upload JSON Key" button in sidebar
- **Cloud**: Add to Secrets (see above)

---

## 🎛️ Configuration

### Environment Variables
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Streamlit Settings
- **Max Pages**: 1-50 (default: 10)
- **Crawl Depth**: 1-3 (default: 2)
- **Timeout**: 10 seconds per page

### Performance Tips
- Use "Quick" preset (3 pages) for testing
- Large sites take longer - start small
- Each entity analysis costs ~$0.01 via Google Cloud
- Monitor your Google Cloud usage

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **ImportError: google-cloud-language** | `pip install google-cloud-language` |
| **Credentials not working** | Verify JSON file is valid, check permissions |
| **Analysis is slow** | Reduce max pages or use Quick preset |
| **Timeout errors** | Website may be blocking requests, try another URL |
| **No entities found** | Check website has text content (not JavaScript-only) |
| **App crashes on deploy** | Check requirements.txt, verify all imports |

---

## 📊 Output Format

CSV file contains:
- **source**: Page URL analyzed
- **name**: Entity name (person, place, organization, etc.)
- **salience**: Importance score (0-1)
- **category**: Entity type (PERSON, LOCATION, ORGANIZATION, etc.)

---

## 📁 Project Structure

```
/Users/aslan/Documents/AIO NLP/
├── streamlit_app.py          # Main Streamlit app
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit config (theme, etc)
└── README.md                # Project documentation
```

---

## 🔗 Useful Links

- **Streamlit Docs**: https://docs.streamlit.io
- **Google Cloud Console**: https://console.cloud.google.com
- **Google NLP API**: https://cloud.google.com/natural-language
- **Streamlit Cloud**: https://streamlit.io/cloud

---

## ✨ Features

✅ Real-time web crawling
✅ Google Cloud NLP entity extraction
✅ CSV export
✅ Interactive UI
✅ Progress tracking
✅ CSV download
✅ Settings persistence
✅ Help & documentation

---

## 💡 Tips & Best Practices

1. **Test locally first** before deploying to cloud
2. **Start with small page counts** to understand behavior
3. **Monitor Google Cloud billing** - NLP API has costs
4. **Keep credentials secure** - never commit them to GitHub
5. **Check website robots.txt** - respect crawling policies
6. **Use presets** for quick testing (Quick = 3 pages, Normal = 10 pages)

---

## 📝 License & Attribution

This is a SEO analysis tool using:
- **Streamlit** - Web app framework
- **BeautifulSoup4** - Web scraping
- **Google Cloud NLP** - Entity extraction
- **Requests** - HTTP client
