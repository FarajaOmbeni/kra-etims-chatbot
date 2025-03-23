from flask import Flask, request, jsonify, current_app
import os
from twilio.twiml.messaging_response import MessagingResponse
from model import generate_answer
app = Flask(__name__)

@app.route("/")
def welcome():
    return "Hello World!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        question = request.values.get("Body", "").lower()
        sender = request.values.get('From', '').replace('whatsapp:', '')

        print(question)

        answer = generate_answer(question)
        
        response = MessagingResponse()
        response.message(answer)

        print(response)

        return str(response)
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return str(MessagingResponse().message("Error occurred"))

if __name__ == "__main__":
    # Check for required environment variables at startup
    if not os.getenv("HUGGINGFACE_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set")
    
    app.run(host='0.0.0.0', debug=True, port=5000)