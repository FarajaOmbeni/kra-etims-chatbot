import requests
from dotenv import load_dotenv
import re
import os
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# API_URL = os.getenv("API_URL")
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = '''
You are a specialized tax assistant designed to answer questions strictly related to tax, the Kenya Revenue Authority (KRA), and the Electronic Tax Invoice Management System (eTIMS) in Kenya. Your responses should be clear, accurate, and up-to-date, relying on official sources where possible.
User Interaction:
At the beginning of the conversation, greet the user warmly and ask for their name to personalize the interaction.
Example: "Hello! I'm your KRA and tax assistant. Before we begin, may I have your name to make our conversation more interactive?"
Address the user by name throughout the conversation to enhance engagement.
If the user asks you their name, look into the conversation history and tell them. Example: Your name is [name]
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

def check_relevancy(question):
    tax_keywords = ["tax", "kra", "etims", "vat", "income tax", "pin", "compliance", "itax", "return", "filing", "penalty", "invoice", "kenya revenue", "pin", "tax", "regulations", "revenue", "turnover tax", "income tax","VAT","file returns","PIN", "tot","eTIMS","invoice","refund","exemption","amend","deadline", "payment",
    "deduction", "certificate","business","income","expenses","audit","registration","update","penalty","submission","report","claims","supporting documents","taxpayer","obligation", "amnesty", "hello", "hi", "hey", "habari", "rate", "day", "file"]

    if any(keyword in question.lower() for keyword in tax_keywords):
        return True

#Function to ask the model
def generate_answer(payload, sender_id, max_tokens=300):
    is_relevant = check_relevancy(payload)

    if not is_relevant:
        return "I'm sorry, I can only answer questions related to taxes, KRA, and eTIMS in Kenya. Please ask a tax-related question."
    
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
    
    tools = {
        'web_search': []
    }

    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=payload,
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0.1,
            tools=[types.Tool(
                google_search=types.GoogleSearchRetrieval
            )]
        )
    )

    # response = completion.choices[0].message.content
    response = response.text
    
    if response:
        clean_response = clean_text(response)
    else:
        clean_response = "Sorry, I couldn't generate a response at this time."

    chat_history[sender_id].append({
        'role': 'assistant',
        'content': clean_response
    })

    print(chat_history)

    return clean_response
