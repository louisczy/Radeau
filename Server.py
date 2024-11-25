#Flask qui permet de créer l'application web
#request qui ermet d'accéder aux données envoyées par le client dans une requête
#jsonify Une réponse JSON que le client peut comprendre.
from flask import Flask, request, jsonify

#Serveur Flask (Création de l'application Flask)
app = Flask(__name__)

#définit une URL (/upload) et les types de requêtes HTTP acceptés(POST)
@app.route('/upload', methods=['POST'])
def upload_data():
    data = request.json #les données JSON envoyées par le client dans la requête
    if data: #les données reçus
        print(f"Reçu: {data}")
        return jsonify({"message": "Données reçues avec succès!"}), 200
    return jsonify({"error": "Aucune donnée reçue"}), 400

#Démarrage du serveur
if __name__ == "__main__":
    print("Démarrage du serveur...")
    app.run(host='127.0.0.1', port=5000)
