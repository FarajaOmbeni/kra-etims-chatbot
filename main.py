from flask import Flask, request, jsonify
import os
from twilio.twiml.messaging_response import MessagingResponse
from model import generate_answer
import model

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
        doc = doc_ref.get()
        past_conversations = doc.to_dict().get('conversations', []) if doc.exists else []
        
        answer = generate_answer(question, past_conversations)
        
        # Store new conversation
        create({'role': 'user', 'content': question}, sender)
        create({'role': 'assistant', 'content': answer}, sender)
        
        response = MessagingResponse()
        response.message(answer)
        return str(response)
    except Exception as e:
        print(f"Error: {str(e)}")
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
def create(data, phone):
   doc_ref = db.collection('chat_records').document(phone)
   doc = doc_ref.get()

   if doc.exists:
       doc_ref.update({
           'conversations': firestore.ArrayUnion([data])
       })
   else:
       doc_ref.set({'conversations': [data]})
       
   return jsonify({'message': 'Document updated successfully', 'document_id': doc_ref.id}), 201

@app.route('/read_all')
def read_all():
    docs = db.collection('chat_records').stream()
    all_docs = {}
    
    for doc in docs:
        all_docs[doc.id] = doc.to_dict()
    
    return jsonify(all_docs), 200

if __name__ == "__main__":
    # Check for required environment variables at startup
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set")
    
    app.run(host='0.0.0.0', debug=True, port=5000)