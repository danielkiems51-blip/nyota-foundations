# PythonAnywhere Deployment Guide: Fuliza Boost

Follow these steps to deploy your **Fuliza Boost** Django application to PythonAnywhere.

## 1. Upload Your Code
The easiest way is to use Git. Open a **Bash Console** on PythonAnywhere and run:

```bash
git clone https://github.com/marcopollo69/FulizaBoost.git
cd FulizaBoost
```

## 2. Set Up Virtual Environment
Creating a virtual environment ensures all dependencies are isolated.

```bash
mkvirtualenv --python=/usr/bin/python3.10 fuliza-venv
pip install -r requirements.txt
```

## 3. Create .env File
On PythonAnywhere, you need to manually create the `.env` file in your project root:

```bash
nano .env
```

Paste your environment variables (copy from your local `.env`):
```text
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=FedhaCred1t.pythonanywhere.com
PYTHONANYWHERE_DOMAIN=FedhaCred1t.pythonanywhere.com
PAYHERO_API_URL=https://backend.payhero.co.ke/api/v2/payments
PAYHERO_CHANNEL_ID=4144
PAYHERO_API_USERNAME=your-username
PAYHERO_API_PASSWORD=your-password
PAYHERO_CALLBACK_URL=https://FedhaCred1t.pythonanywhere.com/api/mpesa/callback/
```
*Note: If you have a free account, PythonAnywhere might block the connection to `payhero.co.ke` unless you request it to be whitelisted.*

## 4. Configure Web App
1. Go to the **Web** tab on PythonAnywhere.
2. Click **Add a new web app**.
3. Select **Manual Configuration** (do NOT choose Django, we will configure the WSGI ourselves).
4. Choose **Python 3.10**.
5. Set the **Virtualenv** path: `/home/FedhaCred1t/.virtualenvs/fuliza-venv`.
6. Set the **Source Code** path: `/home/FedhaCred1t/FulizaBoost`.

## 5. Configure WSGI File
In the **Web** tab, click the link to your **WSGI configuration file**. Replace its entire content with this:

```python
import os
import sys
from dotenv import load_dotenv

# Path to your project
path = '/home/FedhaCred1t/FulizaBoost'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables
os.chdir(path)
load_dotenv(os.path.join(path, '.env'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 6. Static Files
In the **Web** tab, scroll down to the **Static files** section and add:
- **URL:** `/static/`
- **Path:** `/home/FedhaCred1t/FulizaBoost/staticfiles`

Then run this in your console to collect the files:
```bash
python manage.py collectstatic
```

## 7. Database setup
Run migrations to set up your SQLite database:
```bash
python manage.py migrate
```

## 8. Final Step
Go back to the **Web** tab and click **Reload**. Your site should now be live at `FedhaCred1t.pythonanywhere.com`!

---

### ⚠️ Note for Free Accounts
If you see an error related to "Connection Refused" when trying to pay, it is because PythonAnywhere's free tier restricts outbound requests. You will need to upgrade to a "Hacker" plan or ask PythonAnywhere support to whitelist `backend.payhero.co.ke`.
