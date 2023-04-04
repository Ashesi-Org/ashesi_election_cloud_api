import json
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import functions_framework

cred = credentials.Certificate('key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@functions_framework.http
def ashesi_election_http(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request.method == 'GET' and 'stu_id' in request_args:
        return query_student_records()
    elif request.method == 'POST' and 'name' in request_json:
        return create_student_record()
    elif request.method == 'PUT' and 'name' in request_json:
        return update_student_record()
    elif request.method == 'DELETE' and 'name' in request_json:
        return delete_student_record()
    elif request.method == 'GET' and 'elec_id' in request_args:
        return query_election_records()
    elif request.method == 'POST' and 'elec_name' in request_json:
        return create_election_record()
    elif request.method == 'DELETE' and 'elec_name' in request_json:
        return delete_election_record()
    elif request.method == 'POST' and 'candidate' in request_json:
        return create_vote_record()
    else:
        jsonify({'error': 'Request not successful'}), 400

def query_student_records():
    stu_id = request.args.get('stu_id')

    # Get a reference to the Firestore collection
    collection_ref = db.collection('students_data')

    # Query the collection for the student record with the given ID
    query = collection_ref.where('stu_id', '==', stu_id).get()

    # Check if the query returned any results
    if not query:
        return jsonify({'error': 'Data not found'}), 404

    # Convert the first result to a dictionary
    record = query[0].to_dict()

    # Return the student record
    return jsonify(record)

def create_student_record():
    stu_record = json.loads(request.data)

    # Get a reference to the Firestore collection
    collection_ref = db.collection('students_data').document(stu_record['stu_id'])

    # Check if the student record already exists in the collection
    results = collection_ref.get()
    if results.exists:
        return jsonify({'error': 'Student already exists'}), 409

    # Add the student record to the collection
    else:
        collection_ref.set(stu_record)
        return jsonify(stu_record), 201
    
def update_student_record():
    record = json.loads(request.data)

    # Get a reference to the Firestore collection
    collection_ref = db.collection('students_data')

    # Query the collection for the student record with the given ID
    query = collection_ref.where('stu_id', '==', record['stu_id']).get()

    # Check if the query returned any results
    if not query:
        return jsonify({'error': 'Student not found'}), 404

    # Update the first result with the new data
    document_ref = query[0].reference
    document_ref.update({'year': record['year'],
                        'major': record['major']})

    # Get the updated record
    updated_record = document_ref.get().to_dict()

    # Return the updated record
    return jsonify(updated_record)

def delete_student_record():
    record = json.loads(request.data)

    # Get a reference to the Firestore collection
    collection_ref = db.collection('students_data')

    # Query the collection for the student record with the given ID
    query = collection_ref.where('stu_id', '==', record['stu_id']).get()

    # Check if the query returned any results
    if not query:
        return jsonify({'error': 'Student not found'}), 404

    # Delete the first result returned by the query
    query[0].reference.delete()

    # Return the deleted student record
    return jsonify(record)

def query_election_records():
    elec_id = request.args.get('elec_id')

    # Get a reference to the Firestore collection
    collection_ref = db.collection('elections_data')

    # Query the collection for the student record with the given ID
    query = collection_ref.where('elec_id', '==', elec_id).get()

    # Check if the query returned any results
    if not query:
        return jsonify({'error': 'Data not found'}), 404

    # Convert the first result to a dictionary
    record = query[0].to_dict()

    # Return the student record
    return jsonify(record)

def create_election_record():
    elec_record = json.loads(request.data)

    # Get a reference to the Firestore collection
    collection_ref = db.collection('elections_data').document(elec_record['elec_id'])

    # Check if the election record already exists in the collection
    results = collection_ref.get()
    if results.exists:
        return jsonify({'error': 'Election already exists'}), 409

    # Add the election record to the collection
    else:
        collection_ref.set(elec_record)
        return jsonify(elec_record), 201
    
def delete_election_record():
    record = json.loads(request.data)

    # Get a reference to the Firestore collection
    collection_ref = db.collection('elections_data')

    # Query the collection for the election record with the given ID
    query = collection_ref.where('elec_id', '==', record['elec_id']).get()

    # Check if the query returned any results
    if not query:
        return jsonify({'error': 'Election not found'}), 404

    # Delete the first result returned by the query
    query[0].reference.delete()

    # Return the deleted election record
    return jsonify(record)

def create_vote_record():
    vote_record = json.loads(request.data)
    
    # Get references to the Firestore collections
    votes_collection_ref = db.collection('votes_data')
    elections_collection_ref = db.collection('elections_data')
    
    # Check if student record exists
    student_query = db.collection('students_data').where('stu_id', '==', vote_record['stu_id']).get()
    if not student_query:
        return jsonify({'error': 'Student not found'}), 404
    
    # Check if election record exists
    election_query = elections_collection_ref.where('elec_id', '==', vote_record['elec_id']).get()
    if not election_query:
        return jsonify({'error': 'Election not found'}), 404
    
    # Query the votes collection to check if student has already voted
    query = votes_collection_ref.where('stu_id', '==', vote_record['stu_id']).get()
    if query:
        return jsonify({'error': 'Student has already voted'}), 409
    
    # Add the new vote record to the votes collection
    votes_collection_ref.add(vote_record)
    
    # Update the candidate's number of votes in the elections collection
    election_doc = election_query[0].reference
    candidates = election_doc.get().to_dict()['candidates']
    if vote_record['candidate'] in candidates:
        candidates[vote_record['candidate']] += 1
        election_doc.update({'candidates': candidates})
    
    return jsonify(vote_record)

                
                
