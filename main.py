import functions_framework
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

@functions_framework.http
def handle_chat_event(request):
    """
    Handles Google Chat events for an Echo Bot.
    - Greets users when added to a space.
    - Echoes back any message it receives.
    """
    try:
        event_data = request.get_json(silent=True)
        if not event_data:
            logging.warning("Received empty or non-JSON payload.")
            return "Bad Request", 400

        logging.info(f"Received event: {json.dumps(event_data)}")

        event_type = event_data.get('type')
        response_message = {}

        # When the bot is added to a space (or a 1:1 chat), send a greeting.
        if event_type == 'ADDED_TO_SPACE':
            response_message = {"text": "Hi!"}
        
        # When a user sends a message, echo it back.
        elif event_type == 'MESSAGE':
            # Extract the user's message text, stripping any bot mentions.
            user_message = event_data['message']['text'].strip()
            response_message = {"text": user_message}
        
        # For any other event type, do nothing.
        else:
            logging.info(f"Ignored event type: {event_type}")
            return "", 200

        # Send the prepared response back to Google Chat.
        return json.dumps(response_message), 200, {'Content-Type': 'application/json; charset=utf-8'}

    except Exception as e:
        logging.error(f"Error handling request: {e}", exc_info=True)
        # It's a good practice to not send detailed errors back to the user.
        return "", 200
