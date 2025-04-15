from flask import Flask, request, jsonify, current_app
import os
from twilio.twiml.messaging_response import MessagingResponse
from model import generate_answer
import firebase_admin
from firebase_admin import credentials, firestore
from firestore import store_conversation
app = Flask(__name__)

if not firebase_admin._apps:
    cred = credentials.Certificate('./firestore_db.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/")
def welcome():
    return "Hello World!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        question = request.values.get("Body", "").lower()
        sender = request.values.get('From', '').replace('whatsapp:', '')

        print(f"Message from {sender}: {question}")

        #Generate answer
        answer = generate_answer(question, sender)

        #store conversation
        store_conversation(sender, question, answer)

        #Send response via twiltio
        response = MessagingResponse()
        response.message(answer)

        print(response)

        return str(response)
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return str(MessagingResponse().message("Error occurred"))

if __name__ == "__main__":
    # Check for required environment variables at startup
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set")
    
    app.run(host='0.0.0.0', debug=True, port=5000)