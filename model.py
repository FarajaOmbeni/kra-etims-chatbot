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

system_prompt = (
    "You are an expert assistant tasked with answering questions clearly, thoroughly, and accurately. Provide complete and well-structured responses based only on verified information and avoid speculation or fabricated details. If unsure of the answer, respond with 'I don't know' or provide suggestions on where to find reliable information. Always prioritize clarity and correctness in your explanations."
    "When someone greets you, answer politely and ask how you can assist them"
    "You are a helpful assistant named TaxIQ. "
    "If you don't know the answer, admit it rather than guessing. "
    "Always respond as 'Chatbot:' and do not generate 'User:' responses."
)


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
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)

        # Check if response is valid JSON
        try:
            response_data = response.json()
        except ValueError:
            return f"Error: Invalid JSON response: {response.text}"

        # Handle success
        if response.status_code == 200:
            response_data = response.json()  # Make sure to parse the JSON response
            generated_text = response_data[0]['generated_text']
            if generated_text:
                # Remove "User:" from the generated text
                cleaned_text = generated_text.replace("User:", "").strip()

                # Extract the assistant's response
                lines = cleaned_text.split("\n")
                for line in lines:
                    if line.startswith("Chatbot:"):
                        bot_response = line.replace("Chatbot:", "").strip()
                        return bot_response
                else:
                    return "I could not generate a response. Please try again."
        else:
            # Handle API error response
            return f"Error: Request failed with status {response.status_code}: {response.text}"

        
    except requests.Timeout:
        return "I'm sorry, but I'm taking too long to respond. Please try again."
    except Exception as e:
        # Catch any unexpected errors
        print(f"Error in generate_answer: {e}")
        return f"Unexpected error: {e}"

