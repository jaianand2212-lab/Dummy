# GitHub Actions Email Setup Instructions

## 📧 How to Configure Email Notifications

To receive automatic greeting emails after pushing code, you need to set up GitHub Secrets.

### Step 1: Set up GitHub Secrets

1. Go to your repository: https://github.com/jaianand2212-lab/Dummy
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add the following three secrets:

#### Secret 1: EMAIL_USERNAME
- **Name**: `EMAIL_USERNAME`
- **Value**: Your email address (e.g., `your-email@gmail.com`)

#### Secret 2: EMAIL_PASSWORD
- **Name**: `EMAIL_PASSWORD`
- **Value**: Your email app password (see instructions below)

#### Secret 3: EMAIL_TO
- **Name**: `EMAIL_TO`
- **Value**: Email address where you want to receive notifications (e.g., `jan5cob@bosch.com`)

### Step 2: Generate Gmail App Password (if using Gmail)

⚠️ **Important**: Don't use your regular Gmail password!

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left navigation
3. Under "Signing in to Google", enable **2-Step Verification** (if not already enabled)
4. After enabling 2FA, go back to Security page
5. Under "Signing in to Google", click **App passwords**
6. Select **Mail** and **Other (Custom name)**
7. Name it "GitHub Actions"
8. Click **Generate**
9. Copy the 16-character password (remove spaces)
10. Use this as your `EMAIL_PASSWORD` secret in GitHub

### Step 3: Alternative - Use Bosch Email (Outlook/Exchange)

If you want to use your Bosch email:

Update the workflow file to use Bosch SMTP settings:
```yaml
server_address: smtp.office365.com
server_port: 587
```

Then set secrets:
- `EMAIL_USERNAME`: Your Bosch email (e.g., `jan5cob@bosch.com`)
- `EMAIL_PASSWORD`: Your Bosch email password or app password
- `EMAIL_TO`: Your email address

### Step 4: Test the Setup

After configuring secrets, make a test push:

```powershell
git commit --allow-empty -m "Test email notification"
git push
```

Then:
1. Go to **Actions** tab in your GitHub repository
2. Check the workflow run
3. Check your email inbox for the greeting email! 📧

### Email Preview

You will receive a beautiful HTML email with:
- ✅ Success message
- 📋 Commit details (repository, branch, author, message)
- 🔗 Direct link to view the commit on GitHub
- 🎨 Professional styling with colors and formatting

### Troubleshooting

**Email not received?**
- Check GitHub Actions logs for errors
- Verify all three secrets are set correctly
- Check spam/junk folder
- Ensure 2FA and App Password are set up (for Gmail)
- Try using a different email service if one doesn't work

**Using other email providers:**
- **Yahoo**: `smtp.mail.yahoo.com:465`
- **Outlook**: `smtp.office365.com:587`
- **Custom SMTP**: Update server_address and server_port accordingly

---

## 🎉 What Happens Now?

Every time you push code to any branch:
1. GitHub Actions workflow triggers automatically
2. Displays greeting message in Actions logs
3. Sends a beautifully formatted email notification
4. Email includes all commit details and direct link to GitHub

Happy coding! 🚀
