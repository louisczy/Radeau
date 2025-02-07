from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"

@app.route('/')
def home():
    """Affiche la page web avec les données en temps réel."""
    return render_template("page_web.html")

@app.route('/data')
def get_data():
    """Envoie les données JSON pour affichage dynamique."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        if len(data) > 0:
            return jsonify(data[-1])  # Envoie uniquement la dernière valeur
    return jsonify({"temperature": "N/A", "humidity": "N/A", "timestamp": "N/A"})

@app.route('/upload', methods=['POST'])
def upload_data():
    """Réception des données envoyées par le client"""
    client_ip = request.remote_addr
    data = request.json

    if data:
        print(f"Données reçues de {client_ip} : {data}")

        # Sauvegarde des données dans un fichier JSON
        existing_data = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    print("Erreur de lecture du fichier JSON, réinitialisation.")
                    existing_data = []

        existing_data.append(data)

        with open(DATA_FILE, "w") as f:
            json.dump(existing_data, f, indent=4)

        return jsonify({"message": "Données reçues avec succès", "client_ip": client_ip}), 200

    return jsonify({"error": "Aucune donnée reçue"}), 400

if __name__ == "__main__":
    print("Démarrage du serveur HTTP sur 192.168.137.1:5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
