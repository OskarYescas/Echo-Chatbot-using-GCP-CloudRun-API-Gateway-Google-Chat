# Secure Google Chat EchoBot with API Gateway and Cloud Run

This project provides a guide for deploying a minimalistic, secure Google Chat bot. [cite: 3] The architecture uses API Gateway to provide a public endpoint that securely invokes a private Cloud Run service. [cite: 4] This is the best practice for building Chat bots that comply with security policies requiring internal-only services. [cite: 5]

The bot greets users when added to a space and echoes back any message it receives. [cite: 6]

## Architecture Overview

The communication flow is designed to be secure and robust: [cite: 8]

> Google Chat -> [Public API Gateway] -> (Authenticates via IAM) -> [Private Cloud Run Service] [cite: 9]

## Core Technologies

* Python 3 [cite: 11]
* Google Cloud Run (Private) [cite: 12]
* Google Cloud API Gateway [cite: 13]
* Google Chat API [cite: 14]

## Prerequisites

Before you begin, ensure you have the following: [cite: 16]
* A Google Cloud project with billing enabled. [cite: 17]
* A Google Workspace account with permissions to configure Chat apps. [cite: 18]

## Step 1: Enable Required APIs

1.  In the Google Cloud Console, navigate to the "APIs & Services" > "Library". [cite: 20]
2.  Search for and enable each of the following APIs one by one: [cite: 21]
    * Cloud Run API [cite: 22]
    * Google Chat API [cite: 23]
    * Cloud Build API [cite: 25]
    * API Gateway API [cite: 26]
    * Service Management API [cite: 27]
    * Service Control API [cite: 28]

## Step 2: Create a Service Account for API Gateway

This service account acts as the identity for the API Gateway, allowing it to securely invoke your private Cloud Run service. [cite: 31]

1.  Navigate to "IAM & Admin" > "Service Accounts". [cite: 32]
2.  Click "Create Service Account". [cite: 33]
3.  Enter a "Service account name", for example, `api-gateway-sa`. [cite: 34]
4.  Click "Create and Continue", then click "Done". [cite: 35]
5.  Find the service account you just created in the list and copy its email address for later use. [cite: 36]

## Step 3: Deploy the Private Cloud Run Service

Deploy the bot's code to a Cloud Run service that is configured to be private. [cite: 39]

1.  Deploy the service: [cite: 40]
    * Navigate to "Cloud Run" in the Google Cloud Console. [cite: 41]
    * Click "Create Service". [cite: 43]
    * Select "Use an inline editor to create a function". [cite: 45]
    * In the "Service settings": [cite: 47]
        * Give your service a name (e.g., `echobot-private-service`). [cite: 48]
        * Select a region. [cite: 49]
        * Under "Authentication", select "Require authentication". This is critical for making the service private. [cite: 50]
    * Click "Next". [cite: 51]
    * In the editor, paste the Python code provided in Step 6. [cite: 52]
    * Click "Deploy". [cite: 53]
2.  Grant invoke permissions: [cite: 54]
    * After the service deploys, go to its details page. [cite: 56]
    * Click on the "Security" tab. [cite: 57]
    * Under "Authentication", click "Add Principal". [cite: 58]
    * In the "New principals" field, paste the email address of the service account you created in Step 2. [cite: 59]
    * In the "Role" dropdown, select the "Cloud Run Invoker" role. [cite: 60]
    * Click "Save". [cite: 61]

## Step 4: Create and Configure the API Gateway

The API Gateway is the public-facing entry point that securely forwards requests to your private service. [cite: 62]

1.  Create the API Gateway Configuration File: [cite: 63]
    * On your local machine, create a plain text file named `openapi.yaml`. [cite: 64] Using a code editor like VS Code is highly recommended to avoid formatting issues. [cite: 65]
    * Get your private Cloud Run service URL from its details page in the console. [cite: 66]
    * Copy the YAML content below into your file, replacing `[YOUR_PRIVATE_CLOUD_RUN_URL]` in both places with your actual service URL. [cite: 67, 68]

    ```yaml
    swagger: '2.0'
    info:
      title: 'Secure Chatbot Gateway'
      version: '1.0.0'
    schemes:
      - https
    produces:
      - application/json
    paths:
      /:
        post:
          summary: 'Forward requests to the private EchoBot service'
          operationId: 'postRequest'
          x-google-backend:
            address: [YOUR_PRIVATE_CLOUD_RUN_URL]
            jwt_audience: [YOUR_PRIVATE_CLOUD_RUN_URL]
          responses:
            '200':
              description: 'Success'
    ```
    *[YAML content cited from sources 69-82]*

2.  Deploy the API Gateway: [cite: 83]
    * In the Google Cloud Console, navigate to "API Gateway". [cite: 85]
    * Click "Create Gateway". [cite: 86]
    * For "API", select "Create a new API" and give it a display name like `Secure Chatbot API`. [cite: 87]
    * For "API Config", select "Create a new API config". [cite: 88]
        * Click "Browse" and upload the `openapi.yaml` file you just created. [cite: 89]
        * Give the config a display name like `chatbot-config-v1`. [cite: 90]
    * For "Service Account", select the service account you created in Step 2. [cite: 91]
    * Give the gateway a "Display name" (e.g., `secure-chatbot-gateway`) and select the same region as your Cloud Run service. [cite: 92]
    * Click "Create Gateway". This may take a few minutes. [cite: 93]
3.  Get the Gateway's Public URL: [cite: 94]
    * Once the gateway is deployed, go to its details page. [cite: 95]
    * Copy the "Gateway URL". You will need this for the final step. [cite: 96]

## Step 5: Configure the Google Chat API

Point your Chat app to the new secure gateway endpoint. [cite: 98]

1.  Navigate to the "Google Chat API" > "Configuration" page in the Google Cloud Console. [cite: 99]
2.  Fill out the "Application info" (App name, Avatar URL, Description). [cite: 100]
3.  Important: Ensure the checkbox for "Build this Chat as a Workspace add-on" is NOT checked. [cite: 101]
4.  In the "Connection settings" section: [cite: 102]
    * "HTTP endpoint URL": Paste your new API Gateway URL. [cite: 103]
    * "Authentication Audience": Paste the exact same API Gateway URL here. [cite: 104]
5.  Set your desired "Visibility" and click "SAVE". [cite: 105]

## Step 6: The Bot Code (main.py)

This is the Python code for your Cloud Run service. [cite: 107]

```python
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
