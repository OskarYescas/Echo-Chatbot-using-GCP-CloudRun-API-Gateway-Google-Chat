# Secure Google Chat EchoBot with API Gateway and Cloud Run

This project provides a guide for deploying a minimalistic, secure Google Chat bot. The architecture uses API Gateway to provide a public endpoint that securely invokes a private Cloud Run service. This is the best practice for building Chat bots that comply with security policies requiring internal-only services.

The bot greets users when added to a space and echoes back any message it receives.

## Architecture Overview

The communication flow is designed to be secure and robust:

> Google Chat -> [Public API Gateway] -> (Authenticates via IAM) -> [Private Cloud Run Service]

## Core Technologies

* Python 3
* Google Cloud Run (Private)
* Google Cloud API Gateway
* Google Chat API

## Prerequisites

Before you begin, ensure you have the following:
* A Google Cloud project with billing enabled.
* A Google Workspace account with permissions to configure Chat apps.

## Step 1: Enable Required APIs

1.  In the Google Cloud Console, navigate to the "APIs & Services" > "Library".
2.  Search for and enable each of the following APIs one by one:
    * Cloud Run API
    * Google Chat API
    * Cloud Build API
    * API Gateway API
    * Service Management API
    * Service Control API

## Step 2: Create a Service Account for API Gateway

This service account acts as the identity for the API Gateway, allowing it to securely invoke your private Cloud Run service.

1.  Navigate to "IAM & Admin" > "Service Accounts".
2.  Click "Create Service Account".
3.  Enter a "Service account name", for example, `api-gateway-sa`.
4.  Click "Create and Continue", then click "Done".
5.  Find the service account you just created in the list and copy its email address for later use.

## Step 3: Deploy the Private Cloud Run Service

Deploy the bot's code to a Cloud Run service that is configured to be private.

1.  Deploy the service:
    * Navigate to "Cloud Run" in the Google Cloud Console.
    * Click "Create Service".
    * In the "Service settings":
        * Give your service a name (e.g., `echobot-private-service`).
        * Select a region.
        * Under "Authentication", select "Require authentication". This is critical for making the service private.
    * Click "Next".
    * In the editor, paste the Python code provided in the repository and referenced in step 6.
    * Click "Deploy".
2.  Grant invoke permissions:
    * After the service deploys, go to IAM & Admin > IAM.
    * Click "Grant Access".
    * Under "New Principals", add the service account created in step 2.
    * In the "Role" dropdown, select the "Cloud Run Invoker" role.
    * Click "Save".

## Step 4: Create and Configure the API Gateway

The API Gateway is the public-facing entry point that securely forwards requests to your private service.

1.  Create the API Gateway Configuration File:
    * On your local machine, create a plain text file named `openapi.yaml`. 
    * Get your private Cloud Run service URL from its details page in the console.
    * From the file of this repository, use or copy the YAML content into your file, replacing `[YOUR_PRIVATE_CLOUD_RUN_URL]` in both places with your actual service URL. 

2.  Deploy the API Gateway:
    * In the Google Cloud Console, navigate to "API Gateway".
    * Click "Create Gateway".
    * For "API", select "Create a new API" and give it a display name like `Secure Chatbot API` & give it an API ID.
    * For "API Config", select "Create a new API config".
        * Click "Browse" and upload the `openapi.yaml` file you just created.
        * Give the config a display name like `chatbot-config-v1`.
    * For "Service Account", select the service account you created in Step 2.
    * Give the gateway a "Display name" (e.g., `secure-chatbot-gateway`) and select the same region as your Cloud Run service.
    * Click "Create Gateway". This may take a few minutes.
3.  Get the Gateway's Public URL:
    * Once the gateway is deployed, go to its details page.
    * Copy the "Gateway URL". You will need this for the final step.

## Step 5: Configure the Google Chat API

Point your Chat app to the new secure gateway endpoint.

1.  Navigate to the "Google Chat API" > "Configuration" page in the Google Cloud Console.
2.  Fill out the "Application info" (App name, Avatar URL, Description).
3.  Important: Ensure the checkbox for "Build this Chat as a Workspace add-on" is NOT checked.
4.  In the "Connection settings" section:
    * "HTTP endpoint URL": Paste your new API Gateway URL.
    * "Authentication Audience": Select "HTTP endpoint URL".
5.  Set your desired "Visibility" and click "SAVE".

## Step 6: The Bot Code (main.py)

Remember to use the main.py file in the repository for the actual Echo Bot in the cloud function soruce.

## Step 7: Test Your Bot
1. Open Google Chat.
2. Find and add your bot by the name you configured.
3. Send it a message. It should echo your message back, confirming the entire secure flow is working!
