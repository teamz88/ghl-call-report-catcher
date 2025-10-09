# 📞 Call Report Catcher

An automated system that fetches call reports from the TidyYourSales platform and delivers them to an n8n webhook for further processing.

## 📋 What This Does

This tool automates the tedious process of:
1. Logging into TidyYourSales with email and password
2. Requesting and retrieving a security code (OTP) from your email
3. Entering the OTP to complete authentication
4. Navigating to the call reporting dashboard
5. Selecting a date range and downloading call report CSV files
6. Parsing the CSV and sending the data to your n8n webhook
7. **Preventing duplicate sends** - tracks which records have been sent and skips duplicates on subsequent runs

This is especially useful for:
- **Automated daily/hourly reporting workflows** via cron jobs
- **Integrating TidyYourSales data** with other systems (via n8n)
- **Eliminating manual data downloads** and reducing human error

## 🏗️ How It Works

The system consists of 3 main components that run sequentially:

### 1. **app.py** - Email OTP Retrieval
- Connects to Microsoft Graph API (your email account)
- Searches for "Login security code" emails from TidyYourSales
- Extracts the 6-digit OTP code from the email body
- Returns the code to the login automation script

### 2. **login_automation.py** - Main Automation (Entry Point)
- Uses Playwright to automate a Chromium browser
- Logs into TidyYourSales with your credentials
- Requests a security code, then calls `app.py` to retrieve it from email
- Enters the OTP code automatically
- Navigates to the call reporting page
- Sets the date range (configurable, defaults to last 1 day)
- Downloads the report as CSV to the `reports/` folder
- Calls `report_sender.py` to process and send the data

### 3. **report_sender.py** - Data Processing & Webhook Delivery
- Finds the latest CSV file in the `reports/` folder
- Parses the CSV and extracts call records
- **Checks for duplicates** using `dedup_state.json` (persistent across runs)
- Sends only new records to your n8n webhook
- Updates the dedup state after successful delivery

### 🔄 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. login_automation.py starts                               │
│    ↓                                                         │
│ 2. Opens TidyYourSales login page                          │
│    ↓                                                         │
│ 3. Enters email & password → Requests OTP                   │
│    ↓                                                         │
│ 4. Calls app.py to get OTP from email                      │
│    ↓                                                         │
│ 5. Enters OTP → Logs in successfully                       │
│    ↓                                                         │
│ 6. Navigates to call reporting page                         │
│    ↓                                                         │
│ 7. Sets date range & downloads CSV                         │
│    ↓                                                         │
│ 8. Calls report_sender.py                                   │
│    ↓                                                         │
│ 9. Parses CSV → Filters new records → Sends to webhook     │
│    ↓                                                         │
│ 10. Updates dedup_state.json → Done ✅                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

- ✅ **Fully automated login** with OTP verification
- 📧 **Email-based OTP retrieval** via Microsoft Graph API
- 📊 **Flexible date range selection** (custom or automatic)
- 🔗 **n8n webhook integration** for data forwarding
- 🌐 **Headless browser mode** for server deployment
- 🔄 **Smart deduplication** to prevent sending duplicate records
- 📝 **Automatic logging** with timestamped log files
- 🔒 **Lock mechanism** to prevent overlapping runs
- ⚡ **Self-contained** - auto-installs dependencies when using the shell wrapper

## ⚙️ Installation & Setup

### Prerequisites

- **Python 3.8+** installed on your system
- **Microsoft Graph API credentials** (for email OTP retrieval)
  - Requires an Azure AD app registration with `Mail.Read` permissions
  - See [Microsoft Graph Setup](#microsoft-graph-api-setup) below
- **n8n webhook** URL where you want to receive the data
- **TidyYourSales account** with access to call reports

### Step 1: Clone and Install Dependencies

```bash
# Navigate to project directory
cd /path/to/callreportcatcher

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

**Dependencies installed:**
- `playwright` - Browser automation
- `requests` - HTTP requests
- `msal` - Microsoft authentication
- `python-dotenv` - Environment variable management

### Step 2: Configure Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual credentials (see [Configuration Guide](#-configuration-guide) below)

### Step 3: Test the Setup

Run a test to make sure everything works:

```bash
# Test email OTP retrieval
python app.py

# Test the full automation (will open a browser)
python login_automation.py
```

If successful, you should see:
- ✅ Authentication successful
- 📧 OTP code retrieved
- 🎉 Reports successfully sent to webhook

## 🛠️ Configuration Guide

All configuration is done via the `.env` file. Here's what each variable does:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TIDYYOURSALES_EMAIL` | Your TidyYourSales login email | `user@company.com` |
| `TIDYYOURSALES_PASSWORD` | Your TidyYourSales password | `your_password_here` |
| `TIDYYOURSALES_TARGET_URL` | Direct URL to call reporting page<br/>*Must include your location ID* | `https://app.tidyyoursales.com/v2/location/ABC123/reporting/call` |
| `N8N_WEBHOOK_URL` | Your n8n webhook endpoint | `https://n8n.example.com/webhook/call-reports` |

### Microsoft Graph API Configuration

Required for email OTP retrieval:

| Variable | Description | How to Get It |
|----------|-------------|---------------|
| `TENANT_ID` | Azure AD tenant ID | Azure Portal → Azure AD → Overview |
| `CLIENT_ID` | Application (client) ID | Azure Portal → App registrations → Your app |
| `CLIENT_SECRET` | Client secret value | Azure Portal → App registrations → Your app → Certificates & secrets |
| `USER_EMAIL` | Email address to check for OTPs | Same as `TIDYYOURSALES_EMAIL` typically |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER_HEADLESS` | `false` | Set to `true` for server environments (no GUI)<br/>Set to `false` for development (see browser) |
| `REPORT_START_DATE` | Yesterday | Custom start date for reports<br/>Formats: `YYYY-MM-DD` or `MM/DD/YYYY`<br/>Example: `2025-10-01` |
| `REPORT_END_DATE` | Today | Custom end date for reports<br/>Example: `2025-10-08` |
| `TIDYYOURSALES_LOGIN_URL` | `https://app.tidyyoursales.com/` | Only change if TidyYourSales URL changes |
| `REPORTS_FOLDER` | `reports` | Local folder to save CSV files |

### Microsoft Graph API Setup

To enable email OTP retrieval, you need to set up an Azure AD application:

1. **Go to Azure Portal** → Azure Active Directory → App registrations
2. **Click "New registration"**
   - Name: `CallReportCatcher` (or any name)
   - Supported account types: Single tenant
   - Click Register
3. **Copy the Application (client) ID** → This is your `CLIENT_ID`
4. **Copy the Directory (tenant) ID** → This is your `TENANT_ID`
5. **Create a client secret:**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Copy the **Value** (not the ID) → This is your `CLIENT_SECRET`
6. **Add API permissions:**
   - Go to "API permissions"
   - Click "Add a permission" → Microsoft Graph → Application permissions
   - Add: `Mail.Read`
   - Click "Grant admin consent" (requires admin)

## ▶️ Usage

### Run Once (Manual)

```bash
# For development (browser visible)
python login_automation.py

# Using the shell wrapper (recommended)
bash run_call_report.sh
```

### Run on a Schedule (Cron)

The recommended way to use this tool is with cron for automated periodic execution.

1. **Edit your crontab:**
   ```bash
   crontab -e
   ```

2. **Add one of these entries:**

   ```cron
   # Every hour at minute 0
   0 * * * * /bin/bash /Users/bro/PROJECTS/callreportcatcher/run_call_report.sh

   # Every 30 minutes
   */30 * * * * /bin/bash /Users/bro/PROJECTS/callreportcatcher/run_call_report.sh

   # Every day at 9 AM
   0 9 * * * /bin/bash /Users/bro/PROJECTS/callreportcatcher/run_call_report.sh
   ```

3. **Update the path** in the cron command to match your installation directory

**Important:** When using cron:
- Set `BROWSER_HEADLESS=true` in your `.env` file
- Logs will be written to `logs/run_YYYY-MM-DD_HH-MM-SS.log`
- The script won't run if a previous instance is still running (lock mechanism)

### Shell Wrapper Benefits

The `run_call_report.sh` script provides:
- ✅ Automatic virtual environment creation and activation
- ✅ Auto-installation of missing dependencies
- ✅ Timestamped logs in `logs/` directory
- ✅ Lock file to prevent concurrent runs
- ✅ Works reliably in cron (handles PATH issues)

## 📁 Project Structure

```
callreportcatcher/
├── app.py                      # Email OTP retrieval (Microsoft Graph)
├── login_automation.py         # Main automation entry point
├── report_sender.py            # CSV processing & webhook delivery
├── run_call_report.sh          # Shell wrapper for cron/production
├── requirements.txt            # Python dependencies
├── .env                        # Your configuration (DO NOT commit)
├── .env.example                # Example configuration file
├── dedup_state.json            # Tracks sent records (auto-generated)
├── reports/                    # Downloaded CSV files (auto-created)
└── logs/                       # Log files from shell wrapper runs
```

## 🔍 Troubleshooting

### ❌ Authentication Failed / Login Error

**Symptoms:** Script fails at login, can't enter credentials

**Solutions:**
- Verify `TIDYYOURSALES_EMAIL` and `TIDYYOURSALES_PASSWORD` in `.env`
- Check if TidyYourSales changed their login page structure
- Try running with `BROWSER_HEADLESS=false` to see what's happening
- Check if your account requires 2FA or has special security settings

### ❌ OTP Not Found / Email Retrieval Failed

**Symptoms:** "No OTP code found in email" or "Authentication failed"

**Solutions:**
- Verify all Microsoft Graph variables (`TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `USER_EMAIL`)
- Check Azure AD app has `Mail.Read` permission and admin consent granted
- Check if OTP emails are in spam/junk folder (script can't access those)
- Verify sender address in OTP email matches `TARGET_SENDERS` in `app.py` (lines 39-42)
- Wait longer - change the 30-second wait in `login_automation.py:64` if emails are slow

### ❌ Date Picker / Export Button Not Found

**Symptoms:** "Could not find date picker element" or "Export button not found"

**Solutions:**
- TidyYourSales may have updated their UI
- Check the actual page in a browser to see selector changes
- Update the selector lists in `login_automation.py`:
  - `date_picker_selectors` (line 114)
  - `confirm_selectors` (line 228)
  - Export button selector (line 263)

### ❌ Webhook Delivery Failed

**Symptoms:** "Webhook request failed with status XXX"

**Solutions:**
- Verify `N8N_WEBHOOK_URL` is correct and reachable
- Check n8n webhook is active and accepting POST requests
- Test webhook manually with curl:
  ```bash
  curl -X POST "YOUR_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}'
  ```
- Check firewall/network settings if running on a server
- Look at n8n logs to see if it's receiving the request

### ❌ Browser Not Found / Playwright Error

**Symptoms:** "Executable doesn't exist" or "Browser not found"

**Solutions:**
```bash
# Reinstall Playwright browsers
playwright install

# Or install specific browser
playwright install chromium
```

### ❌ Duplicate Records Being Sent

**Symptoms:** Same records sent multiple times to webhook

**Solutions:**
- Check if `dedup_state.json` exists and is readable/writable
- Make sure the script completes successfully (webhook send must succeed)
- If you want to reset and resend everything:
  ```bash
  rm dedup_state.json
  ```

### 🔍 Debugging Tips

1. **Run with visible browser:**
   ```bash
   # Edit .env
   BROWSER_HEADLESS=false

   # Then run
   python login_automation.py
   ```

2. **Check log files:**
   ```bash
   # View latest log
   ls -lt logs/ | head -5
   cat logs/run_YYYY-MM-DD_HH-MM-SS.log
   ```

3. **Test components individually:**
   ```bash
   # Test email OTP only
   python app.py

   # Test webhook delivery only (requires CSV in reports/)
   python report_sender.py
   ```

4. **Increase wait times:**
   - If pages load slowly, increase `asyncio.sleep()` values in `login_automation.py`

## 🔒 Security Best Practices

- ✅ **Never commit `.env` file** - It contains sensitive credentials
- ✅ **Use environment-specific `.env` files** - Different for dev/staging/prod
- ✅ **Rotate credentials regularly** - Change passwords and client secrets periodically
- ✅ **Use minimal permissions** - Azure AD app should only have `Mail.Read`, nothing more
- ✅ **Restrict webhook access** - Use authentication on your n8n webhook if possible
- ✅ **Keep logs secure** - Log files may contain sensitive information
- ✅ **Use service accounts** - Don't use personal email accounts for production

## 📊 Data Flow & Deduplication

### How Deduplication Works

The system uses `dedup_state.json` to track which records have been sent:

1. Each CSV record is hashed (SHA256) based on all its fields
2. Before sending, the hash is checked against `dedup_state.json`
3. Only new records (not in the state file) are sent to webhook
4. After successful webhook delivery, new hashes are added to the state file

**Example `dedup_state.json`:**
```json
{
  "ids": [
    "a1b2c3d4e5f6...",
    "f6e5d4c3b2a1...",
    ...
  ]
}
```

### Webhook Payload Format

The data sent to your n8n webhook looks like this:

```json
{
  "timestamp": "2025-10-08T14:30:00.123456",
  "total_reports": 5,
  "reports": [
    {
      "Date & Time": "2025-10-08 10:30:15",
      "Caller": "+1234567890",
      "Duration": "00:03:45",
      "Status": "Answered",
      ...
    },
    ...
  ]
}
```

The `reports` array contains the actual CSV data as JSON objects.

## 🤝 Contributing

If you improve this tool:
1. Update this README with your changes
2. Update `CLAUDE.md` if you change the architecture
3. Test thoroughly before committing
4. Document any new environment variables in `.env.example`

## 📝 License

*For internal use only*

---

**Need help?** Check the troubleshooting section above or review log files in `logs/` directory.
