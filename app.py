import json
import os
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

travel_custom_functions = [
    {
        'name': 'extract_student_info',
        'description': 'Get the information of a trip from the description of a project',
        'parameters': {
            'type': 'object',
            'properties': {
                'departureDate': {
                    'type': 'string',
                    'description': 'Date of the departure in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour'
                },
                'arrivalDate': {
                    'type': 'string',
                    'description': 'Date of the arrival in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour; if not included take the same as the departure : departureDate'
                },
                'departureReturnDate': {
                    'type': 'string',
                    'description': 'Date of the return departure in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour'
                },
                'arrivalReturnDate': {
                    'type': 'string',
                    'description': 'Date of the return arrival in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour; if not included take the same as the departure : departureReturnDate'
                },
                'numberPersons': {
                    'type': 'integer',
                    'description': 'Number of persons'
                },
                'citiDeparture': {
                    'type': 'string',
                    'description': 'City of departure'
                },
                'citiArrival': {
                    'type': 'string',
                    'description': 'City of arrival'
                },
            }
        }
    }
]

client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)

@app.route('/extract_info', methods=['POST'])
@cross_origin()
def extract_info():
    data = request.json  # Obtient les données de la requête POST
    messages = [{'role': 'user', 'content': data.get('description', '')}]
    
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        functions=travel_custom_functions,
        function_call='auto'
    )

    print(response.choices[0].message.function_call.arguments)
    
    return json.loads(response.choices[0].message.function_call.arguments)


@app.route('/conversation', methods=['POST'])
@cross_origin()
def conversation():
    data = request.json
    print("on a reçu ça:")  # Obtient les données de la requête POST
    print( data.get('description', ''))
    messages = [{'role': 'user', 'content': data.get('description', '')}]
    
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
    )


    print("On est passé on envoie ça :")
    print(response.choices[0].message.content)
    message_content = response.choices[0].message.content
    return  jsonify({"response": message_content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Lancer l'application Flask
