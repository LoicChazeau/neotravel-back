<a name="readme-top"></a>

<br />
<div align="center">
  <a href="https://github.com/LoicChazeau/neotravel-back">
    <img src="logo.svg" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Neotravel - Back</h3>
  <p align="center">
    Développement d'un Chatbot pour Neotravel
    <br />
    <br />
    <a href="https://neotravel-front.vercel.app">Chatbot</a>
    <br />
    <a href="https://g162578.learnai.fr">Web site (Wordpress)</a>
    <br />
    <a href="https://neotravel-back-indol.vercel.app/">API du Chatbot</a>
  </p>
</div>

## NeoTravel Chatbot

Ce projet implémente un chatbot pour le site de location de voyage en bus NeoTravel. Le chatbot utilise OpenAI pour générer des réponses basées sur les messages des utilisateurs et Airtable pour gérer les données des devis.

## Prérequis

- Python 3.x
- Flask
- openai
- pyairtable
- flask-cors
- requests
- dotenv

## Installation

1. Installez les dépendances.

    ```bash
    pip install -r requirements.txt
    ```

2. Configurez les variables d'environnement en créant un fichier `.env` à la racine du projet avec le contenu suivant :

    ```env
    OPENAI_API_KEY=your_openai_api_key
    AIRTABLE_API_KEY=your_airtable_api_key
    AIRTABLE_APP_ID=your_airtable_app_id
    AIRTABLE_TABLE_ID=your_airtable_table_id
    ```

## Lancer l'application

Pour démarrer l'application Flask :

```bash
python app.py
```

## Auteurs

- Loïc Chazeau
- Guillaume Ravan Nalbandian
- Quentin Taverne
- Ngone Ba




