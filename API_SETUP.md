# API Integration Setup Guide

## Overview
This guide explains how to set up WhatsApp (Twilio) and Google Chat integrations for the contact form.

## Prerequisites
- Python environment with packages: `flask`, `gunicorn`, `twilio`, `requests`, `python-dotenv`
- Install with: `pip install -r requirements.txt`

## 1. Twilio WhatsApp Setup

### Step 1: Create Twilio Account
1. Go to https://www.twilio.com/console
2. Sign up for a free account (includes $10 trial credit)
3. Verify your phone number

### Step 2: Get Credentials
1. On the Twilio Console, note your **Account SID** and **Auth Token**
2. Go to "Messaging" → "Try it out" → "Send an SMS"
3. Request WhatsApp access (or visit Messaging → Channels → WhatsApp)
4. Note the Twilio WhatsApp number provided (e.g., +1234567890)

### Step 3: Verify Your Recipient Number
1. In Twilio Console, go to "Messaging" → "WhatsApp" → "Senders"
2. Add recipient number (+27795510741) to approved recipients list
3. Follow verification steps (you'll receive a WhatsApp message)

### Step 4: Update .env
Create a `.env` file in the project root:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+1234567890
```

## 2. Google Chat/Hangouts Webhook Setup

### Step 1: Create Google Chat Webhook
1. Open Google Chat
2. Create or select a space where you want to receive messages
3. Go to Space settings → Apps & integrations → Create new webhook
4. Name it "Portfolio Contact Form"
5. Copy the webhook URL

### Step 2: Update .env
Add to your `.env` file:
```
GOOGLE_CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/XXXXXXXXXXXXXXXX/messages?key=...
```

## 3. Local Development Testing

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create .env File
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### Run Flask App
```bash
python app.py
```

### Test Contact Form
1. Visit http://localhost:5000/contact
2. Fill in the form
3. Select a channel (WhatsApp, Google Hangouts, or Email)
4. Submit
5. Check your WhatsApp or Google Chat for the message

## 4. Production Deployment (Render)

### Add Environment Variables to Render
1. Go to your Render deployment settings
2. Under "Environment", add:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_NUMBER`
   - `GOOGLE_CHAT_WEBHOOK_URL`
   - `RECIPIENT_WHATSAPP_NUMBER`
   - `RECIPIENT_EMAIL`

3. Deploy your app

## 5. Troubleshooting

### WhatsApp Messages Not Sending
- ✓ Check Twilio Account SID and Auth Token are correct
- ✓ Verify recipient number is approved in Twilio
- ✓ Ensure Twilio account has sufficient balance or trial credit
- ✓ Check for error messages in application logs

### Google Chat Messages Not Sending
- ✓ Verify webhook URL is correct and not expired
- ✓ Check Google Chat space still accepts webhooks
- ✓ Look for HTTP 401/403 errors in app logs

### Local vs Production Differences
- Local: Uses environment variables from `.env` file
- Production (Render): Uses environment variables from Render dashboard
- Never commit `.env` file to git (it's in `.gitignore`)

## 6. Cost Estimates

### Twilio
- Free trial: $10 credit
- After trial: ~$0.0079 per WhatsApp message (varies by country)
- Monthly minimum typically $20 if not using free tier

### Google Chat
- Completely free via webhooks

## 7. Email Integration (Future)

Email support is marked as TODO. To implement:
- Use SendGrid, AWS SES, or similar service
- Add API key to environment variables
- Update `messaging.py` `send_email()` method

## File Structure

```
portfolio_site/
├── app.py              # Flask application with contact route
├── messaging.py        # Messaging service (WhatsApp, Google Chat)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (DO NOT COMMIT)
├── .env.example       # Example of required variables
├── static/
│   └── style.css      # Includes chat-success and chat-error styles
└── templates/
    ├── base.html      # Master template
    └── contact.html   # Contact form
```

## Testing Checklist

- [ ] Twilio account created and verified
- [ ] WhatsApp number approved as sender and recipient
- [ ] Google Chat webhook created (optional)
- [ ] `.env` file created with all required variables
- [ ] `pip install -r requirements.txt` runs successfully
- [ ] `python app.py` starts without errors
- [ ] Contact form loads at `/contact`
- [ ] Submitting form with WhatsApp channel sends message
- [ ] Submitting form with Google Hangouts sends message
- [ ] Messages appear on page with success/error indicator
- [ ] Messages received on WhatsApp/Google Chat
