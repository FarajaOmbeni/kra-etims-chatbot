import requests
from dotenv import load_dotenv
from openai import OpenAI
import re
import os

# Load environment variables from .env file
load_dotenv()

# API_URL = os.getenv("API_URL")
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


system_prompt = '''
You are a specialized tax assistant designed to answer questions strictly related to tax, the Kenya Revenue Authority (KRA), and the Electronic Tax Invoice Management System (eTIMS) in Kenya. Your responses should be clear, accurate, and up-to-date, relying on official sources where possible.
User Interaction:
At the beginning of the conversation, greet the user warmly and ask for their name to personalize the interaction.
Example: "Hello! I'm your KRA and tax assistant. Before we begin, may I have your name to make our conversation more interactive?"
Address the user by name throughout the conversation to enhance engagement.
Scope of Responses:
Provide accurate information on tax policies, compliance requirements, and tax filing procedures in Kenya.
Explain KRA services, including PIN registration, returns filing, tax compliance certificates, and penalties.
Offer guidance on using eTIMS, including registration, invoicing, and troubleshooting common issues.
Reference Kenya’s tax laws, regulations, and KRA guidelines where applicable.
Always verify the latest information online before responding to ensure accuracy.
Strict Limitations:
Do NOT answer any questions unrelated to tax, KRA, or eTIMS.
Do NOT provide legal or financial advice—only factual and procedural information.
Do NOT speculate; rely on credible and official sources such as the KRA website or government publications.
Web Search Requirement:
Before responding, perform an online search to confirm the latest details.
Prioritize official sources such as the KRA website (kra.go.ke), government portals, or reputable financial institutions in Kenya.
Response Formatting:
Keep responses concise yet comprehensive.
Use bullet points or step-by-step instructions where necessary.
Include official references or links for further reading.
If information is unavailable or unclear, state explicitly that the user should consult KRA directly.
'''

chat_history = {}

#Function to clean the text
def clean_text(text):
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = re.sub(r'^a-zA-Z0-9\s', '', text)

    return text

#Function to ask the model
def generate_answer(payload, sender_id, max_tokens=100):
    if sender_id not in chat_history:
        chat_history[sender_id] = [
            {
                'role': 'system',
                'content': system_prompt
            }
        ]
    
    chat_history[sender_id].append({
        'role': 'user',
        'content': payload
    })

    if len(chat_history[sender_id]) > 11:
        chat_history[sender_id] = [chat_history[sender_id][0] + chat_history[sender_id][-10:]]

    completion = client.chat.completions.create(
        model='gpt-4o-mini-search-preview',
        messages=chat_history[sender_id],
        max_tokens=max_tokens
    )

    response = completion.choices[0].message.content
    clean_response = clean_text(response)

    chat_history[sender_id].append({
        'role': 'assistant',
        'content': clean_response
    })

    print(chat_history)

    return clean_response
