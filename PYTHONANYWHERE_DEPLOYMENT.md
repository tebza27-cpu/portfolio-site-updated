# Deploy to PythonAnywhere

PythonAnywhere is Python-specific hosting with a free tier. This guide walks through deploying your portfolio site.

## Step 1: Create a PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Sign up for a free account
3. Log in to your dashboard

## Step 2: Upload Your Code to PythonAnywhere

**Option A: Using Git (Recommended)**

1. In PythonAnywhere, open a **Bash Console** (Consoles tab → Bash)
2. Clone your repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/portfolio-site.git
   ```
   (Replace with your actual GitHub repo URL — if it's private, you'll need to set up SSH keys)

**Option B: Upload via Web**

1. Go to **Files** tab
2. Upload your project files directly

## Step 3: Create a Web App

1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Python 3.11**
4. Confirm the domain (e.g., `yourname.pythonanywhere.com`)

## Step 4: Configure WSGI File

PythonAnywhere creates a WSGI file automatically. You need to update it:

1. In the **Web** tab, under your web app, click the **WSGI configuration file** link
2. Replace the contents with:

```python
import sys
import os

# Add your project directory to the path
path = '/home/YOUR_USERNAME/portfolio-site'
if path not in sys.path:
    sys.path.append(path)

# Set up the Flask app
from app import app as application
```

3. Save the file (Ctrl+S or File → Save)

## Step 5: Set Up a Virtual Environment

1. Go to **Web** tab → Your web app section
2. Scroll to **Virtualenv** section
3. Click **Enter path to a virtualenv** and enter:
   ```
   /home/YOUR_USERNAME/.virtualenvs/portfolio-venv
   ```
4. Click the link to create a new virtualenv (choose Python 3.11)

Wait for it to complete (~1-2 minutes).

## Step 6: Install Dependencies

1. Open a **Bash Console**
2. Activate the virtualenv and install packages:
   ```bash
   cd portfolio-site
   source /home/YOUR_USERNAME/.virtualenvs/portfolio-venv/bin/activate
   pip install -r requirements.txt
   ```

## Step 7: Configure Static Files

1. In the **Web** tab, scroll to **Static files** section
2. Add a static file mapping:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/portfolio-site/static`

## Step 8: Set File Paths for OneDrive Access

**Important:** Your app references local OneDrive paths (e.g., `C:\Users\User\OneDrive...`). These paths **won't exist** on PythonAnywhere's Linux server.

**Solution:** Update `app.py` to use environment variables or disable local file viewing on PythonAnywhere:

Option 1: Use environment variables (recommended)
```python
# In app.py, replace hardcoded paths with:
import os

ONEDRIVE_BASE_PATH = os.getenv('ONEDRIVE_PATH', r"C:\Users\User\OneDrive - BYU-Pathway Worldwide\BYU")

ALLOWED_PATHS = [
    os.getenv('BYU_PATH', r"F:\BYU"),
    os.getenv('DOCS_PATH', r"C:\Users\User\OneDrive - BYU-Pathway Worldwide\Documents"),
    os.getenv('RECORDINGS_PATH', r"C:\Users\User\OneDrive - BYU-Pathway Worldwide\Recordings")
]
```

Then in PythonAnywhere Web Console:
1. Click **Web** → Your app
2. Scroll to **Environment variables**
3. Add: 
   - `ONEDRIVE_PATH` = `/home/YOUR_USERNAME/portfolio-site/data`
   - `BYU_PATH` = `/home/YOUR_USERNAME/portfolio-site/data`
   - etc.

Option 2: Disable local file viewing (simpler)
- The app will still work; users just see OneDrive links and recordings
- Local file viewing won't be available remotely (it's a secondary feature)

## Step 9: Reload Your Web App

1. In the **Web** tab
2. Click the green **Reload** button at the top

## Step 10: Visit Your Site

Your app is now live at: `https://YOUR_USERNAME.pythonanywhere.com`

Test it:
- Go to `/projects` to see the course links and recordings
- Click on OneDrive links to verify they work
- If you set up local paths, click on file names to view them

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
- Virtualenv isn't activated. Check Step 5 and ensure the virtualenv path is correct in the **Web** tab.

### "No such file or directory" errors
- Local file paths don't exist. Either upload them or use Option 2 (disable local viewing).

### Static files not loading
- Check the **Static files** mapping in Step 7.

### 404 or 500 errors
- Check **Error log** in the **Web** tab → scroll to **Log files** section
- Open `/home/YOUR_USERNAME/portfolio_site_pythonanywhere_com_wsgi.log`

### App doesn't update after changes
- Click **Reload** in the **Web** tab after each change

## Optional: Use a Custom Domain

1. In the **Web** tab, under **Domains** section
2. Add your custom domain (requires DNS configuration)
3. Update SSL certificate (free via Let's Encrypt)

## Keep Your App Running

- Free tier: App sleeps after 100 seconds of inactivity (wakes on next request)
- Paid tier: Always-on option available

Your portfolio site is now live and publicly accessible! 🚀
