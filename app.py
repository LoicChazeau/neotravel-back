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

Fonctionnalités Clés du Bot :

    Informations Générales :
        Répondre aux questions générales sur les types de services offerts, les zones desservies, et les options disponibles pour chaque type de transport. Les messages doivent être stylé au format HTML pour être utilisé dans une box de message côté front. La box n'est pas très large il faut donc souvent revenir à la ligne en utilisant <br>. les listes doivent être du style <ul> <li> </li> </ul>.

    Demande de Devis :
        Aider les utilisateurs à soumettre une demande de devis en ligne en leur fournissant des instructions sur les informations nécessaires (dates, nombre de passagers, destinations, etc.).

    Contact et Support :
        Fournir les coordonnées pour contacter le service client, les horaires d'ouverture, et les moyens de communication disponibles (téléphone, email, formulaire en ligne).

    Engagements de l'Entreprise :
        Informer les utilisateurs sur les engagements de l'entreprise en matière de sécurité, de législation, et de protection de l'environnement.

    Réglementation et Sécurité :
        Expliquer les mesures de sécurité en place pour les trajets, ainsi que les certifications et les assurances associées aux services de transport.

Utilisation des Services du Bot :

    Exemple de Question sur le Transport Scolaire :
        Utilisateur : "Quels sont les services disponibles pour le transport scolaire ?"
        Bot : "Autocar-Location.com propose des services de transport régulier pour les élèves et les étudiants, assurant leur sécurité et confort. Pour plus d'informations ou pour demander un devis, veuillez visiter notre page dédiée."

    Exemple de Question sur les Événements Professionnels :
        Utilisateur : "Pouvez-vous organiser le transport pour un séminaire professionnel ?"
        Bot : "Oui, nous offrons des solutions de transport pour les séminaires, conférences, et autres événements professionnels. Nos autocars peuvent être équipés selon vos besoins spécifiques. Pour en savoir plus, visitez cette page."

    Exemple de Demande de Devis :
        Utilisateur : "Comment puis-je obtenir un devis pour une excursion ?"
        Bot : "Pour demander un devis, veuillez remplir le formulaire en ligne sur notre site. Assurez-vous de fournir toutes les informations nécessaires telles que les dates, le nombre de passagers, et les destinations."
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
        'content': ("Vous êtes un assistant qui répond uniquement en français. Vous devez aider l'utilisateur "
                    "à naviguer sur notre site de location de voyage en bus : NeoTravel. Si l'utilisateur demande "
                    "utilisez la fonction 'estimate' pour l'indiquer à notre front page. Si l'utilisateur demande à "
                    "parler à un humain, utilisez la fonction 'askCommercial' pour l'indiquer à notre front page. "
                    "Voici des informations sur les services proposés par NeoTravel : " + prompt)
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
