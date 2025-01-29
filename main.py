from flask import Flask, request, jsonify, current_app
import os
from twilio.twiml.messaging_response import MessagingResponse
from model import generate_answer, system_prompt
from threading import Thread

import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        question = request.values.get("Body", "").lower()
        sender = request.values.get('From', '').replace('whatsapp:', '')
        
        # Get past conversations
        doc_ref = db.collection('chat_records').document(sender)
        try:
            doc = doc_ref.get()
            conversation_sessions = doc.to_dict().get('conversations', []) if doc.exists else []
        except Exception as e:
            print(f"Firestore error: {e}")
            conversation_sessions = []

        # Prepare payload for the generate_answer function
        payload = {
            "inputs": f"System Prompt: {system_prompt} \n User: {question} \nChatbot:",
            "parameters": {
                "max_new_tokens": 1000,
                "stop": ["User:", "Chatbot:"]
            }
        }

        print(f"Payload: {payload}")
        
        answer = generate_answer(payload, conversation_sessions)
        
        response = MessagingResponse()
        response.message(answer)

        new_conversation = [
            {"from": "human", "value": question},
            {"from": "gpt", "value": answer}
        ]

        Thread(target=async_store_conversation, args=(new_conversation, sender)).start()

        return str(response)
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return str(MessagingResponse().message("Error occurred"))

cred = credentials.Certificate('./firestore_db.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
    
@app.route('/read/<document_id>')
def read(document_id):
    doc_ref = db.collection('chat_records').document(document_id)
    doc = doc_ref.get()

    if doc.exists:
        data = jsonify(doc.to_dict())
        return data, 200
    else:
        return jsonify({'error': 'Document not found'}), 404

@app.route('/create', methods=['POST'])
def async_store_conversation(conversation, phone):
    with app.app_context():
        doc_ref = db.collection('chat_records').document(phone)
        try:
            doc = doc_ref.get()
            new_entry = {"conversations": conversation}

            if doc.exists:
                doc_ref.update({
                    'conversation_sessions': firestore.ArrayUnion([new_entry])
                })
            else:
                doc_ref.set({'conversation_sessions': [new_entry]})
                
            return jsonify({'message': 'Document updated successfully', 'document_id': doc_ref.id}), 201
        except Exception as e:
            print(f"Error storing conversation: {e}")

@app.route('/read_all')
def read_all():
    docs = db.collection('chat_records').stream()
    all_docs = {}
    
    for doc in docs:
        all_docs[doc.id] = doc.to_dict()
    
    return jsonify(all_docs), 200

if __name__ == "__main__":
    # Check for required environment variables at startup
    if not os.getenv("HUGGINGFACE_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set")
    
    app.run(host='0.0.0.0', debug=True, port=5000)