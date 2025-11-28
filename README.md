# 📊 Basket Range Analysis App

A Streamlit application for analyzing Basket Size Distribution with AI-powered insights

## 🚀 Features

- 📈 **Analysis Report**: Comprehensive basket range comparison (SPLY vs Current)
- 🤖 **AI Summary**: Strategic insights and actionable recommendations powered by GPT-4o-mini
- 🎨 **Dark Theme**: Professional BI Dashboard UI
- 📊 **Custom Metrics**: ABR, Sales, Share%, Bills tracking
- 🔐 **Secure Login**: Password-protected interface

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Database**: Google BigQuery
- **AI**: OpenAI GPT-4o-mini
- **Data Processing**: Pandas

## 📦 Installation

### Local Development

1. Clone repository:
```bash
git clone <your-repo-url>
cd basket-range
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup secrets in `.streamlit/secrets.toml`:
```toml
# App Password
APP_PASSWORD = "your-password"

# OpenAI API Key
OPENAI_API_KEY = "sk-proj-..."

# BigQuery Service Account
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Key\n-----END PRIVATE KEY-----\n"
client_email = "your-email@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

4. Run the app:
```bash
streamlit run app.py
```

## ☁️ Streamlit Cloud Deployment

### 1. Prepare GitHub Repository

Make sure these files are ready in your repo:
- ✅ `app.py` (uses st.secrets)
- ✅ `requirements.txt`
- ✅ `.gitignore`

**Important:** Never commit these files:
- ❌ `.streamlit/secrets.toml`
- ❌ `*.json` (BigQuery credentials)
- ❌ `app_localhost.py`

### 2. Push Code to GitHub

```bash
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main
```

### 3. Configure Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Login with your GitHub account
3. Click "New app"
4. Configure:
   - **Repository:** `basket-range`
   - **Branch:** `main`
   - **Main file path:** `app.py`

### 4. Add Secrets to Streamlit Cloud

1. Navigate to **App settings** → **Secrets**
2. Paste content from `.streamlit/secrets.toml` (see example above)
3. Click "Save"

### 5. Deploy!

Click **"Deploy!"** and wait a moment. Your app will be deployed to Streamlit Cloud.

## 🔐 BigQuery Setup

### Getting Service Account Credentials

1. Open your `your-project-credentials.json` file
2. Copy the values into the secrets format shown above:
   - `type`, `project_id`, `private_key_id`, `private_key`, `client_email`, etc.
3. **Important:** `private_key` must include `\n` for line breaks

## 📝 Usage

1. Login with password
2. Select date range (Start Date - End Date)
3. Enter filters (optional):
   - Supplier Code(s)
   - Category Name(s)
   - Sub-Category Name(s)
   - Brand Name(s)
4. Click "🚀 Run Analysis"
5. View results and AI insights

## 🔧 Troubleshooting

### Issue: "Module not found"
**Solution:** Verify that `requirements.txt` contains all necessary dependencies

### Issue: "Connection refused" or "Authentication error"
**Solution:** Check your Secrets configuration:
- Correct TOML format
- Contains `[gcp_service_account]`, `OPENAI_API_KEY`, and `APP_PASSWORD`
- Private key has proper `\n` for line breaks

### Issue: "Protobuf version conflict"
**Solution:** Ensure `requirements.txt` includes `protobuf<5` and `numpy<2`

## ✅ Pre-Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] No secrets/credentials files in repo
- [ ] `app.py` uses `st.secrets` throughout
- [ ] `requirements.txt` has all dependencies
- [ ] Secrets added to Streamlit Cloud
- [ ] Ready to Deploy!

## 🔒 Security Notes

- **Never commit** `.streamlit/secrets.toml` or BigQuery `.json` files
- Use `.gitignore` to exclude sensitive files
- For production, use environment variables or Streamlit secrets
- Change default password in secrets

## 📄 License

Data Analyst Automation Projects - YodaWagyu
