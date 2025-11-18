# 📧 Email Notification Troubleshooting Guide

## ❌ Problem: Not Receiving Emails from GitHub Actions

Follow these steps to diagnose and fix the issue:

---

## Step 1: Check GitHub Actions Workflow Status

1. Go to your repository: https://github.com/jaianand2212-lab/Dummy
2. Click on the **"Actions"** tab
3. Click on the latest workflow run
4. Check if the workflow succeeded or failed
5. Click on **"Send Greeting Email"** step to see error messages

### Common Errors:
- ❌ **Authentication failed** → Wrong password or username
- ❌ **Connection timeout** → Wrong SMTP server or port
- ❌ **Secrets not found** → Secrets not configured

---

## Step 2: Verify GitHub Secrets Are Configured

Go to: https://github.com/jaianand2212-lab/Dummy/settings/secrets/actions

### Required Secrets (Must have exactly 3):

| Secret Name | Status | What It Should Be |
|-------------|--------|-------------------|
| `EMAIL_USERNAME` | ⬜ Check if exists | Your email address (e.g., `yourname@gmail.com`) |
| `EMAIL_PASSWORD` | ⬜ Check if exists | Gmail App Password (16 characters, no spaces) |
| `EMAIL_TO` | ⬜ Check if exists | Where to receive email (e.g., `jan5cob@bosch.com`) |

### How to Add/Update Secrets:
1. Click **"New repository secret"** or edit existing ones
2. Name must be EXACT: `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_TO`
3. Value must not have extra spaces or quotes
4. Click **"Add secret"** or **"Update secret"**

---

## Step 3: Gmail App Password Setup (Most Common Issue!)

### ⚠️ IMPORTANT: You CANNOT use your regular Gmail password!

### Generate Gmail App Password:

1. **Enable 2-Factor Authentication First:**
   - Go to: https://myaccount.google.com/security
   - Under "Signing in to Google", enable **"2-Step Verification"**
   - Follow the prompts to set it up

2. **Generate App Password:**
   - After 2FA is enabled, go to: https://myaccount.google.com/apppasswords
   - Or navigate: Google Account → Security → 2-Step Verification → App passwords
   - Select **"Mail"** as the app
   - Select **"Other (Custom name)"** as the device
   - Enter name: "GitHub Actions"
   - Click **"Generate"**
   - **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)
   - Remove spaces: `abcdefghijklmnop`

3. **Use This in GitHub Secret:**
   - Secret Name: `EMAIL_PASSWORD`
   - Secret Value: `abcdefghijklmnop` (no spaces!)

---

## Step 4: Test Email Configuration Locally

You can test if your email credentials work before using them in GitHub Actions:

### Quick Python Test:
```python
import smtplib
from email.mime.text import MIMEText

# Replace with your values
EMAIL_USERNAME = "yourname@gmail.com"
EMAIL_PASSWORD = "your_app_password_here"
EMAIL_TO = "jan5cob@bosch.com"

try:
    msg = MIMEText("Test email from Python")
    msg['Subject'] = "Test Email"
    msg['From'] = EMAIL_USERNAME
    msg['To'] = EMAIL_TO
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run this in PowerShell:
```powershell
python -c "import smtplib; print('SMTP library available')"
```

---

## Step 5: Alternative Email Providers

### If Gmail doesn't work, try these:

#### Option A: Microsoft Outlook/Bosch Email

Update `.github/workflows/greeting.yml`:
```yaml
server_address: smtp.office365.com
server_port: 587
```

Secrets:
```
EMAIL_USERNAME = jan5cob@bosch.com
EMAIL_PASSWORD = your_bosch_password
EMAIL_TO = jan5cob@bosch.com
```

#### Option B: Yahoo Mail

Update workflow:
```yaml
server_address: smtp.mail.yahoo.com
server_port: 587
```

Generate Yahoo App Password: https://login.yahoo.com/account/security

---

## Step 6: Check Spam/Junk Folder

- Emails might be going to **Spam** or **Junk** folder
- Check all folders in your email client
- Add `noreply@github.com` or your `EMAIL_USERNAME` to safe senders

---

## Step 7: Simplified Workflow for Testing

Create a minimal test workflow to isolate the issue:

File: `.github/workflows/test-email.yml`
```yaml
name: Test Email Only

on:
  workflow_dispatch:  # Manual trigger

jobs:
  test-email:
    runs-on: ubuntu-latest
    steps:
      - name: Send Test Email
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 587
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: "Test Email from GitHub Actions"
          to: ${{ secrets.EMAIL_TO }}
          from: ${{ secrets.EMAIL_USERNAME }}
          body: |
            This is a test email.
            If you receive this, your configuration is correct!
```

Trigger manually:
1. Go to Actions tab
2. Click "Test Email Only"
3. Click "Run workflow"

---

## Step 8: Common Mistakes Checklist

- [ ] Secret names are spelled EXACTLY: `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_TO`
- [ ] Gmail App Password is 16 characters (no spaces)
- [ ] 2-Factor Authentication is enabled for Gmail
- [ ] Email address is correct (no typos)
- [ ] No extra spaces in secret values
- [ ] SMTP server and port match your email provider
- [ ] Corporate firewall/proxy not blocking SMTP

---

## Step 9: Debug Mode

To see more details in workflow logs, update the email step:

```yaml
- name: Send Greeting Email
  uses: dawidd6/action-send-mail@v3
  env:
    ACTIONS_STEP_DEBUG: true
  with:
    # ... rest of configuration
```

---

## Quick Fix Solutions

### Solution 1: Use Gmail with App Password (Recommended)

1. Enable Gmail 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Set secrets:
   ```
   EMAIL_USERNAME = yourname@gmail.com
   EMAIL_PASSWORD = 16-char-app-password (no spaces)
   EMAIL_TO = jan5cob@bosch.com
   ```

### Solution 2: Use Bosch Email

1. Update workflow SMTP settings to Office365
2. Set secrets:
   ```
   EMAIL_USERNAME = jan5cob@bosch.com
   EMAIL_PASSWORD = your_bosch_password
   EMAIL_TO = jan5cob@bosch.com
   ```

### Solution 3: Use a Different Email Action

Replace `dawidd6/action-send-mail@v3` with:
```yaml
- name: Send email
  uses: cinotify/github-action@main
  with:
    to: ${{ secrets.EMAIL_TO }}
    subject: 'Code Push Successful'
    body: 'Greetings! You successfully pushed code.'
  env:
    SMTP_HOST: smtp.gmail.com
    SMTP_PORT: 587
    SMTP_USERNAME: ${{ secrets.EMAIL_USERNAME }}
    SMTP_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
```

---

## Need Help?

1. **Check workflow logs:** https://github.com/jaianand2212-lab/Dummy/actions
2. **Verify secrets exist:** https://github.com/jaianand2212-lab/Dummy/settings/secrets/actions
3. **Test email locally first** using the Python script above
4. **Check spam folder** in your email
5. **Try a different email provider** if one doesn't work

---

## Working Configuration Example

Here's a confirmed working setup:

**Workflow (in `.github/workflows/greeting.yml`):**
```yaml
uses: dawidd6/action-send-mail@v3
with:
  server_address: smtp.gmail.com
  server_port: 587
  username: ${{ secrets.EMAIL_USERNAME }}
  password: ${{ secrets.EMAIL_PASSWORD }}
  subject: "Test Email"
  to: ${{ secrets.EMAIL_TO }}
  from: ${{ secrets.EMAIL_USERNAME }}
  body: "Test message"
```

**GitHub Secrets:**
- `EMAIL_USERNAME`: `yourname@gmail.com`
- `EMAIL_PASSWORD`: `abcdefghijklmnop` (16-char Gmail App Password)
- `EMAIL_TO`: `recipient@example.com`

This should work 100% if configured correctly! 🎉
