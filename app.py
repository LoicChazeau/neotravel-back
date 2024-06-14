import json
import os
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from pyairtable import Api
import time
import requests

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


prompt = """
Tu es un assistant qui répond uniquement en français. Vous devez aider l'utilisateur à naviguer sur notre site de location de voyage en bus : NeoTravel.
Ne cite pas directement les informations tu peux reformuler.
Si l'utilisateur demande un devis ou le prix d'un voayge utiliser la fonction 'estimate' pour l'indiquer à notre front page.
Si l'utilisateur demande à parler à un humain ou à nous téléphoner, utilisez la fonction 'askCommercial' pour l'indiquer à notre front page.
Les réponses seront affiché dans une boîte de dialogue interprété en HTML. Applique du style aux réponses pour les rendre le plus lisible possible, ex : utilisation de <ul> et <li> pour les listes.
Voici des informations sur NeoTravel : 
Autocar-Location.com propose une gamme complète de services de location d'autocars adaptés à divers besoins de transport pour les entreprises, les associations, les collectivités et les particuliers. Voici un résumé des services disponibles :

    Transport Scolaire et Universitaire :
        Service de transport régulier pour les élèves et les étudiants, assurant la sécurité et le confort des trajets scolaires et universitaires.

    Excursions et Voyages Touristiques :
        Organisation de circuits touristiques, excursions d'une journée ou voyages plus longs. Les destinations populaires incluent les parcs d'attractions, les sites historiques, et les événements culturels.

    Transferts Aéroport et Gare :
        Service de navette pour les transferts vers et depuis les aéroports et les gares, idéal pour les groupes et les délégations.

    Événements Professionnels et Entreprises :
        Transport pour les séminaires, conférences, congrès, et autres événements professionnels. Les autocars peuvent être équipés de commodités spécifiques selon les besoins de l'entreprise.

    Mariages et Événements Privés :
        Solutions de transport pour les mariages, fêtes familiales, et autres événements privés, offrant confort et commodité pour tous les invités.

    Transport de Personnes à Mobilité Réduite :
        Services adaptés pour les personnes à mobilité réduite, avec des autocars équipés pour assurer l'accessibilité et le confort.

    Tourisme d'Affaires et Voyages Incentive :
        Organisation de voyages d'affaires et de programmes incentive pour les entreprises, combinant transport et activités de team-building.

    Type de véhicules :
    NOS VÉHICULES 

    Chez autocar location, nous vous proposons différents types de véhicules en fonction du nombre de passagers :
    Location d’un minibus avec chauffeur pour les groupes comptant moins de 19 personnes
    Un minicar avec chauffeur pour les groupes de 20 à 38 personnes
    Location d’un autocar, d’un bus avec chauffeur pour les groupes de 38 à 65 personnes
    L’autocar grand tourisme, grande capacité, à double étage pour les groupes de 66 à 93 personnes.

    Réglementation :
    Le respect de la réglementation des temps de conduite est l’affaire de tous, ni les organisateurs, ni les transporteurs ne doivent faire prendre de risques aux passagers et aux conducteurs. L’intégrité étant l’une de nos valeurs fortes, la Société NEOTRAVEL, dont Autocar-Location.com fait partie, ne travaille qu’avec des autocaristes qui respectent la réglementation sociale en vigueur. Cette ligne de conduite est au cœur des préoccupations de nos équipes dans la gestion des opérations de transports et dans le conseil à nos clients.

    La durée maximum de conduite continue
        La conduite continue ne doit pas dépasser 4h30 durant la journée et 3h pendant la nuit.
        Au delà un arrêt de 45mn doit être respecté, éventuellement fractionné en deux périodes, la première étant alors de 15mn et la seconde de 30mn.
    La durée maximum de conduite journalière
        Un chauffeur ne doit pas dépasser 9h de conduite journalière.
        La durée de conduite peut être portée à 10h maximum deux fois par semaine et par conducteur.
    Temps de repos journalier
        Le temps de repos journalier est de 11h consécutives pouvant être :
        réduite à 9 heures consécutives au minimum, dans la limite de 3 fois entre deux repos hebdomadaires ;
        fractionnée en deux périodes, dont la première doit être une période ininterrompue de 3 heures au moins, suivie d’une seconde période ininterrompue d’au moins 9 heures.
    L’amplitude et son dépassement
        L’amplitude de la journée de travail d’un conducteur est la période comprise entre le début et la fin de sa journée de travail.
        Cette amplitude peut atteindre 12h au total pour un conducteur seul.
        Elle peut être parfois exceptionnellement portée à 14h sous conditions règlementaires extrêmement précises.
        Au delà de 14h d’amplitude et jusqu’à 18h il est donc nécessaire de mettre à disposition un deuxième chauffeur.
    Le repos hebdomadaire
        Le repos est applicable après 6 jours consécutifs de travail en France comme à l’étranger.
        La durée de repos hebdomadaire doit être égale à 45h consécutives.
        Il est possible de prendre une semaine sur deux un repos réduit à 24h sous condition de rattrapage du repos réduit
        L’obligation d’un repos de 45h se fait au moins une fois tous les 15 jours.

    Engagement :
        Engagement de l'entreprise : "Nous travaillons pour que les générations futures bénéficient de moyens de transports respectueux de l’environnement. C’est la raison pour laquelle nous nous engageons pour la planète, et nous avons rejoint le Club PME du WWF France."



"""

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
        "description":"Detecte lorsque l'utilisteur demande un devis ou une estimation. ex : 'demande de devis', 'je veux un devis' 'combien coûte un trajet ?'"
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
    historique = data.get("historique",'')
    lastMessage = data.get('description', '')
    
    message_system = {
        'role': 'system', 
        'content': (prompt)
    }

    # Ajouter le message système au début de l'historique
    messages = [message_system] + historique

    # Ajouter le dernier message de l'utilisateur à la fin de la liste des messages
    messages.append({'role': 'user', 'content': lastMessage})

    print(messages)
    
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
    # urlWebhook = record["fields"]["Url_webhook"]
    # response = requests.request("GET", urlWebhook)
    # print("WebHook :")
    # print(response.text)


    toReturn = {'success': True, 'id': record["id"]}
    print(toReturn)
    return jsonify(toReturn)

@app.route('/sendFeedback', methods=['POST'])
@cross_origin()
def sendFeedback():
    data = request.json
    id = data["id"]
    feedback = data["feedback"]
    table.update(id,{"Feedback":feedback})


    return jsonify({"sucess":"sucess"})

@app.route('/getPdf', methods=['GET'])
@cross_origin()
def getPdf():
    id = request.args.get('id')
    print(id)
    record = table.get(record_id=id)
    i = 0

    if "ID" in record['fields']:
        while i < 7:
            print("ON A SLEEP MDR")
            i += 1
            record = table.get(record_id=record["id"])
            if "Quote_pdf" in record['fields']:
                break
            time.sleep(1)
        
        if "Quote_pdf" not in record['fields']:
            print("ON pas A LE PDF MDR LOLILOL")
            toReturn = { 'success': False, 'id': record["id"], "pdf_url": None }
            return jsonify(toReturn)
    toReturn = { 'success': True, 'id': record["id"], "pdf_url": record['fields']['Quote_pdf'][0]['url']}
    print(toReturn)
    return jsonify(toReturn)

@app.route('/test', methods=['GET'])
@cross_origin()
def test():
    toReturn = { 'success': "success"}
    return jsonify(toReturn)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Lancer l'application Flask
