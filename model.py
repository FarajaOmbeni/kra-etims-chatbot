import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_URL = os.getenv("API_URL")
api_key = os.getenv("HUGGINGFACE_API_KEY")

headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

#Function to ask the model
def generate_answer(payload, past_conversation=None, max_tokens=300):
    try:
        # Validate API key
        if not api_key:
            raise ValueError("API key is not set in environment variables")

        # Print payload for debugging
        print("Payload sent to API:", payload)

        # Make the API request
        response = requests.post(API_URL, headers=headers, json=payload)

        # Check if response is valid JSON
        try:
            response_data = response.json()
        except ValueError:
            return f"Error: Invalid JSON response: {response.text}"

        # Handle success
        if response.status_code == 200:
            generated_text = response_data[0]['generated_text']
            if "Chatbot:" in generated_text:
                bot_response = generated_text.split("Chatbot:")[1].strip()
                print(f"Bot response: {bot_response}")
                return bot_response
            else:
                return "I could not generate a response. Please try again."
        else:
            # Handle API error response
            return f"Error: Request failed with status {response.status_code}: {response.text}"

    except Exception as e:
        # Catch any unexpected errors
        print(f"Error in generate_answer: {e}")
        return f"Unexpected error: {e}"

