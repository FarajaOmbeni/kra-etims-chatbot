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

conversation_sessions = []

#Function to ask the model
def generate_answer(payload, past_conversation=None, max_tokens=300):
    global conversation_sessions
    try:
        # Validate API key
        if not api_key:
            raise ValueError("API key is not set in environment variables")  
           
        new_session = {
            "conversations": [
                {
                    "from": "human",
                    "value": payload['inputs']
                }
            ]
        }       

        if past_conversation:
            for session in past_conversation:
                if session not in conversation_sessions:
                    conversation_sessions.extend(session)

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
                new_session["conversations"].append(
                    {
                        "from": "gpt",
                        "value": bot_response
                    }
                )
                conversation_sessions.append(new_session)
                print(f"Bot response: {bot_response}")
                print(f"Conversations: {conversation_sessions}")
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

