# 📞 Call Report Catcher

A system to automatically fetch call reports from the TidyYourSales platform and send them to an n8n webhook.

## 🚀 Features

- 🔐 Automatic login with OTP
- 📧 Retrieve OTP code via email
- 📊 Download CSV reports
- 🔗 n8n webhook integration
- 🌐 Browser automation with Playwright

## ⚙️ Installation

### 1. Install dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 2. Run the automation
```bash
python login_automation.py
```

## 📁 File Structure

```
callreportcatcher/
├── 🔧 app.py                 # Email OTP retrieval via Microsoft Graph
├── 🤖 login_automation.py    # Main automation flow
├── 📤 report_sender.py       # Process CSV and send to webhook
├── ⚙️ .env                   # Environment variables
└── 📊 reports/               # Downloaded CSV files
```

## 🔄 Workflow

1. **🔐 Login** — Sign in to the TidyYourSales platform
2. **📧 OTP** — Get the OTP code from email and verify
3. **📊 Report** — Download the latest daily report
4. **📤 Send** — Send the data to the n8n webhook

## 🛠️ Configuration

All settings are in the .env file:

- `TIDYYOURSALES_EMAIL` — Login email
- `TIDYYOURSALES_PASSWORD` — Password
- `N8N_WEBHOOK_URL` — Webhook URL
- `BROWSER_HEADLESS` — Browser mode (true/false)

Optional (depending on your setup):
- `TIDYYOURSALES_LOGIN_URL` — Login URL for TidyYourSales
- `TIDYYOURSALES_TARGET_URL` — Target page URL for call reporting
- `REPORTS_FOLDER` — Local folder to store downloaded CSV files

Microsoft Graph API (for email OTP retrieval):
- `TENANT_ID`
- `CLIENT_ID`
- `CLIENT_SECRET`
- `USER_EMAIL`

## 🔍 Troubleshooting

### ❌ Login error
- Verify email and password
- Confirm the target URL is correct

### ❌ OTP not found
- Check your email configuration
- Look in the spam folder

### ❌ Webhook error
- Verify the n8n webhook URL
- Check your internet connection

## 🔒 Security

- Never commit the `.env` file to git
- Rotate passwords regularly
- Use minimal required permissions

## ▶️ Running and Scheduling

Run once:
```bash
bash /Users/bro/PROJECTS/callreportcatcher/run_call_report.sh
```

Schedule with cron (examples):
- Every hour:
```cron
0 * * * * /bin/bash /Users/bro/PROJECTS/callreportcatcher/run_call_report.sh
```
- Every 30 minutes:
```cron
*/30 * * * * /bin/bash /Users/bro/PROJECTS/callreportcatcher/run_call_report.sh
```

Notes:
- The runner loads .env, auto-installs missing Python dependencies and Playwright browsers, writes logs to logs/, and prevents overlapping runs.
- Set BROWSER_HEADLESS=true in .env for server environments.

---
*For internal use only*