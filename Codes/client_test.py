import time
import requests

def send_data():
 server_url ="http://192.168.137.2:5000/upload"
 while True:
        data = {
          "temperature":22,
          "humidity": 50,
          "timestamp": time.time()
        }
        try:
            response = requests.post(server_url, json=data)
            if response.status_code == 200:
                print("Données envoyées avec succès")
            else:
                print(f"Erreur lors de lenvoi: {response.status_code}")
        except Exception as e:
               print(f"Erreur de connexion: {e}")
        time.sleep(5)



if __name__ == "__main__":
    print("Demarrage du client..")
    send_data()
