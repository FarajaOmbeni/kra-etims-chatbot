import firebase_admin
from firebase_admin import credentials, firestore
from flask import request, jsonify

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