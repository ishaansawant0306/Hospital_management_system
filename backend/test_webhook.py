from tasks import send_google_chat_webhook

if __name__ == "__main__":
    print("Testing Google Chat Webhook...")
    try:
        send_google_chat_webhook("👋 Hello! If you see this, your Webhook is working perfectly!")
        print("Message sent! Check your Google Chat.")
    except Exception as e:
        print(f"Failed to send: {e}")
