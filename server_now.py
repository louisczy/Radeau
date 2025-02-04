from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_data():
    # Récupérer l'adresse IP du client
    client_ip = request.remote_addr

    # Récupérer les données JSON envoyées par le client
    data = request.json
    if data:
        # Loguer les données reçues et l'adresse IP du client
        print(f"Données reçues de {client_ip} : {data}")
        return jsonify({
            "message": "Données reçues avec succès",
            "client_ip": client_ip
        }), 200

    # Gérer le cas où aucune donnée n'est reçue
    print(f"Requête vide reçue de {client_ip}")
    return jsonify({"error": "Aucune donnée reçue"}), 400

if __name__ == "__main__":
    print("Démarrage du serveur HTTP sur 192.168.137.1:5000...")
    # Démarrer le serveur Flask sur l'adresse IP et le port spécifiés
    app.run(host='0.0.0.0', port=5000)