import os
import json
import requests

# Get secrets from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') # e.g., "@yourchannelname" or "-100123456789"

def handler(event, context):
    # Ensure this function is only callable via POST
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Telegram token or chat ID not configured'})
        }

    try:
        # Parse the incoming JSON body
        body = json.loads(event.get('body', '{}'))
        message_text = body.get('message')

        if not message_text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "message" in request body'})
            }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON body'})
        }

    # Telegram API URL
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message_text,
        'parse_mode': 'MarkdownV2' # Optional: or 'HTML' or remove for plain text
    }

    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)

        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'status': 'Message sent successfully!', 'telegram_response': response.json()})
        }
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        # If Telegram returns an error, it might be in e.response.text or e.response.json()
        error_details = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details = e.response.text
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'error': 'Failed to send message', 'details': error_details})
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'error': 'An unexpected error occurred', 'details': str(e)})
        }

# For local testing (optional, if you run `python send_telegram.py` directly)
# if __name__ == '__main__':
#     # Mock event for local testing
#     # Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as environment variables first!
#     # export TELEGRAM_BOT_TOKEN="your_token"
#     # export TELEGRAM_CHAT_ID="your_chat_id"
#     if not os.environ.get('TELEGRAM_BOT_TOKEN') or not os.environ.get('TELEGRAM_CHAT_ID'):
#         print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables for local testing.")
#     else:
#         test_event = {
#             'httpMethod': 'POST',
#             'body': json.dumps({'message': 'Hello from local Python script!'})
#         }
#         response = handler(test_event, None)
#         print(response)