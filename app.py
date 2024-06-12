import json
import os
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

app = Flask(__name__)

cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)

airTableToken = os.environ['AIRTABLE_API_KEY']
app_id = os.environ['AIRTABLE_APP_ID']
table_id = os.environ['AIRTABLE_TABLE_ID']

airtable = Api(airTableToken)
table = airtable.table(app_id, table_id)

# rows = table.all()

travel_custom_functions = [
    # {
    #     'name': 'extract_trip_info',
    #     'description': 'Get the information of a trip from the description of a project',
    #     'parameters': {
    #         'type': 'object',
    #         'properties': {
    #             'departureDate': {
    #                 'type': 'string',
    #                 'description': 'Date of the departure in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour'
    #             },
    #             'arrivalDate': {
    #                 'type': 'string',
    #                 'description': 'Date of the arrival in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour; if not included take the same as the departure : departureDate'
    #             },
    #             'departureReturnDate': {
    #                 'type': 'string',
    #                 'description': 'Date of the return departure in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour'
    #             },
    #             'arrivalReturnDate': {
    #                 'type': 'string',
    #                 'description': 'Date of the return arrival in format yyyy-MM-dd ex: "2024-06-12" if the year is not stated, take the current one, do not include hour; if not included take the same as the departure : departureReturnDate'
    #             },
    #             'numberPersons': {
    #                 'type': 'integer',
    #                 'description': 'Number of persons'
    #             },
    #             'citiDeparture': {
    #                 'type': 'string',
    #                 'description': 'City of departure'
    #             },
    #             'citiArrival': {
    #                 'type': 'string',
    #                 'description': 'City of arrival'
    #             },
    #         }
    #     }
    # },
    {
        "name":"estimate",
        "description":"Detecte lorsque l'utilisteur demande un devis ou une estimation"
    },
    {
        "name":"askCommercial",
        "description":"Detecte lorsque l'utilisteur demande à échanger avec nos équipes. Ou quand l'utilsateur veut parler à un humain. Ou quand l'utilisateur veut nous téléphoner"
    },
]


@app.route('/conversation', methods=['POST'])
@cross_origin()
def conversation():
    data = request.json
    # Obtient les données de la requête POST
    messages = [
        {'role': 'system', 'content': "Vous êtes un assistant qui répond uniquement en français. Vous devez aider l'utilsiateur a naviguer sur notre site de location de voyage en bus : NeoTravel. Si l'utilisateur demande utilisez la fonction 'estimate' pour l'indiquer à notre front page. Si l'utilisateur demande à parler à un humain utilise la fonction 'askCommercial pour l'indiquer à notre front page'"},
        {'role': 'user', 'content': data.get('description', '')}
    ]
    
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        functions=travel_custom_functions,
        function_call='auto'
    )
    print("Demande :")
    print(data.get('description', ''))
    print("Réponse :")
    if response.choices[0].message.function_call==None:
        print("Conversation")
        toReturn = {
            "type":"conversation",
            "response":response.choices[0].message.content
        }
    else:
        print("Function")
        toReturn = {
            "type":"functionCall",
            "functionName":response.choices[0].message.function_call.name
        }
    print(toReturn)

    return jsonify(toReturn)

@app.route('/sendDevis', methods=['POST'])
@cross_origin()
def sendDevis():
    data = request.json
    record = table.create(data)
    toReturn = { 'success': True, 'id': record["id"] }
    return jsonify(toReturn)


@app.route('/test', methods=['GET'])
@cross_origin()
def test():
    toReturn = { 'success': "success"}
    return jsonify(toReturn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Lancer l'application Flask
