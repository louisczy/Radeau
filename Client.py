import time
import requests #Pour envoyer des requêtes HTTP (GET, POST, etc.) vers un serveur

def send_data():
    server_url = "http://127.0.0.1:5000/upload"  # URL du serveur local
    while True: #Envoie continuellement des données au serveur
        # Simuler des données de capteurs
        data = {
            "temperature": 22,
            "humidity": 50,
            "timestamp": time.time()
        }
        try:
            response = requests.post(server_url, json=data) #Envoi des données au serveur type POST et convertie data en JSON
            if response.status_code == 200:
                print("Données envoyées avec succès!")
            else:
                print(f"Erreur lors de l'envoi: {response.status_code}")
        except Exception as e:
            print(f"Erreur de connexion: {e}")
        time.sleep(5)  # Envoyer des données toutes les 5 secondes
        
#Vérifie si le fichier est exécuté 
#Démarrage du client
if __name__ == "__main__":
    print("Démarrage du client...")
    send_data()
