# 🚀 Deploy to Streamlit Cloud

Your code is now ready to deploy! Follow these steps:

## Step 1: Create GitHub Repository

### Using GitHub Web Interface (Easiest)
1. Go to https://github.com/new
2. Create a new repository:
   - Name: `seo-crawler-pro`
   - Description: "Advanced SEO entity analysis tool"
   - Privacy: **Public** (required for free Streamlit Cloud tier)
   - Do NOT initialize with README (we have one locally)
3. Click **Create repository**

### Get Remote URL
After creating the repo, GitHub will show commands like:
```
git remote add origin https://github.com/YOUR_USERNAME/seo-crawler-pro.git
git branch -M main
git push -u origin main
```

---

## Step 2: Push Code to GitHub

Copy-paste these commands in your terminal:

```bash
cd /Users/aslan/Documents/AIO\ NLP

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/seo-crawler-pro.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Important:** Replace `YOUR_USERNAME` with your actual GitHub username!

---

## Step 3: Deploy on Streamlit Cloud

1. Go to **https://streamlit.io/cloud**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select:
   - **Repository**: `YOUR_USERNAME/seo-crawler-pro`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click **Deploy**

Streamlit will deploy your app and give you a URL like:
```
https://seo-crawler-pro.streamlit.app
```

---

## Step 4: Add Google Cloud Credentials (Secrets)

1. In Streamlit Cloud dashboard, click your app
2. Go to **Settings** → **Secrets**
3. Paste your Google Cloud JSON content as plain JSON:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-email@project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "your-cert-url"
}
```

4. Click **Save**

---

## Step 5: Test Your App

1. Visit your app URL
2. Upload Google Cloud credentials
3. Enter a test website (e.g., `https://example.com`)
4. Click "LAUNCH ANALYSIS"
5. View results and visualizations!

---

## 🎉 You're Live!

Your app is now publicly available at:
```
https://seo-crawler-pro.streamlit.app
```

Share the link with anyone!

---

## 📝 Making Updates

Every time you push to GitHub, Streamlit automatically redeploys:

```bash
# Make changes locally
git add .
git commit -m "Update description"
git push
```

Your app updates automatically! ✨

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"App not found"** | Repository must be public |
| **"Credentials error"** | Verify JSON format in Secrets |
| **"ModuleNotFoundError"** | Check `requirements.txt` has all dependencies |
| **"Timeout"** | Reduce max pages or increase Streamlit timeout |

---

## 💡 Pro Tips

- **Free Tier Limits**: 1GB RAM, limited concurrent apps
- **Google Cloud Costs**: Monitor your usage (entity extraction ~$0.01 each)
- **Rate Limiting**: Don't crawl massive sites in quick succession
- **Billing Alerts**: Set up Google Cloud alerts to avoid surprises

---

## 🔗 Useful Links

- Streamlit Cloud: https://streamlit.io/cloud
- GitHub: https://github.com
- Google Cloud Console: https://console.cloud.google.com
- Streamlit Docs: https://docs.streamlit.io

---

**Your app is ready to deploy! 🚀**