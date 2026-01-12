# Google API Setup Guide

## Prerequisites
- Google Cloud Console account
- Python with required packages installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID

## Step 2: Enable APIs

Enable the following APIs for your project:
- **Google Calendar API**: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
- **Gmail API**: https://console.cloud.google.com/apis/library/gmail.googleapis.com

## Step 3: Create OAuth 2.0 Credentials

1. Go to [Credentials page](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Configure OAuth consent screen if prompted:
   - User Type: External (for personal use) or Internal (for organization)
   - App name: JARVIS
   - User support email: Your email
   - Developer contact: Your email
   - Add scopes: `calendar` and `gmail.modify`
   - Add test users (your email)
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: JARVIS Desktop Client
5. Download the JSON file
6. Rename it to `google_credentials.json`
7. Place it in `credentials/` directory

## Step 4: Configure Environment Variables

Update your `.env` file:

```bash
# Google API Configuration
GOOGLE_CREDENTIALS_PATH=credentials/google_credentials.json
GOOGLE_TOKEN_PATH=credentials/google_token.json
GOOGLE_CALENDAR_ID=primary
GMAIL_USER_EMAIL=me
```

## Step 5: First-Time Authentication

When you first run the Calendar or Gmail MCP server:

1. A browser window will open automatically
2. Sign in with your Google account
3. Grant the requested permissions
4. The token will be saved to `credentials/google_token.json`
5. Future runs will use this token (no browser needed)

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Make sure you added your email as a test user in OAuth consent screen
- Verify the scopes are correctly configured

### "Token has been expired or revoked"
- Delete `credentials/google_token.json`
- Run the server again to re-authenticate

### "Credentials file not found"
- Verify the path in `.env` matches your actual file location
- Make sure the JSON file is valid

## Security Notes

⚠️ **Important**:
- Never commit `google_credentials.json` to version control
- Never commit `google_token.json` to version control
- Both files are already in `.gitignore`
- Keep these files secure and private

## Scopes Used

### Calendar
- `https://www.googleapis.com/auth/calendar` - Full calendar access

### Gmail
- `https://www.googleapis.com/auth/gmail.modify` - Read, send, and modify emails

## Testing

Test the servers:

```bash
# Test Calendar
curl http://localhost:8004/tools

# Test Gmail
curl http://localhost:8005/tools
```

## References

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
