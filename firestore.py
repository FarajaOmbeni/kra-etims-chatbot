import firebase_admin
from firebase_admin import credentials, firestore
from flask import request, jsonify
from datetime import datetime

cred = credentials.Certificate('./firestore_db.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection('chat_records').document('example@gmail.com')

def create():
    data = request.json()
    if data:
        doc_ref.set(data)
        return jsonify({'message': 'Document created succesfully', 'document_id': doc_ref[1].id}), 201
    else:
        return jsonify({'error':'No data provided'}), 400

def store_conversation(sender, question, answer):
    """Store conversation in Firestore database"""
    try:
        # Reference to the user's document
        user_ref = db.collection('chat_records').document(sender)
        
        # Get current timestamp
        timestamp = datetime.now()
        
        # Create conversation data
        conversation_data = {
            'timestamp': timestamp,
            'question': question,
            'answer': answer
        }
        
        # Check if user document exists
        user_doc = user_ref.get()
        
        if user_doc.exists:
            # Update existing document with new conversation
            user_ref.update({
                'conversations': firestore.ArrayUnion([conversation_data]),
                'last_interaction': timestamp
            })
        else:
            # Create new document for the user
            user_ref.set({
                'phone_number': sender,
                'conversations': [conversation_data],
                'created_at': timestamp,
                'last_interaction': timestamp
            })
            
        print(f"Conversation stored for user {sender}")
        return True
        
    except Exception as e:
        print(f"Error storing conversation: {str(e)}")
        return False