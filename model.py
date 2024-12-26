from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def generate_answer(question, past_conversation=None):
    try:
        # Check if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is not set in environment variables")

        client = OpenAI(api_key=api_key)

        conversations = [
            {
                "role": "system",
                "content": "You are a helpful bot and all you know is teaching about tax. You can answer any legal question you are asked, and nothing else. When a user sends greetings, Ask them for their name and email address one by one and say you are looking for previous conversations if there are. If the user asks for their name, tell them their name",
            },
        ]

        if past_conversation:
            conversations.extend(past_conversation)

        conversations.append(
            {
                "role": "user",
                "content": question,
            }
        )

        response = client.chat.completions.create(
            messages=conversations,
            model="gpt-4o-mini",
            max_tokens=500,  # Limit response length
            timeout=30,  # Set timeout for API calls
        )

        assistant_response = response.choices[0].message.content

        conversations.append(
            {
                "role": "assistant",
                "content": assistant_response
            }
        )

        print(conversations)
        return assistant_response

    except ValueError as e:
        # Handle configuration errors
        print(f"Configuration error: {str(e)}")
        return "I'm sorry, but I'm not properly configured at the moment. Please contact support."

    except OpenAI.APIError as e:
        # Handle API errors
        print(f"OpenAI API error: {str(e)}")
        return "I'm having trouble connecting to my knowledge base. Please try again in a few moments."

    except OpenAI.APITimeoutError:
        # Handle timeout errors
        print("Request timed out")
        return "I'm taking too long to respond. Please try again."

    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {str(e)}")
        return "I encountered an unexpected error. Please try again later."