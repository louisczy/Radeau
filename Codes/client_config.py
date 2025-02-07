import time
import json
import requests
from datetime import datetime, timedelta
import pandas as pd  # Import pour l'archivage Excel et CSV
import sys  # Import pour gestion de l'encodage
import os  # Import pour gestion des fichiers
import matplotlib.pyplot as plt  # Import pour la visualisation

################################Configuration######################################################################
SERVER_URL ="http://192.168.137.2:5000/upload"# URL du serveur
LOCAL_STORAGE_FILE = "data.json"  # Fichier pour stocker les données localement
# Charger la configuration depuis un fichier JSON
def charger_configuration(fichier_config):
    try:
        with open(fichier_config, "r") as fichier:
            config = json.load(fichier)
            print(f"Configuration chargée avec succès : {config}")
            return config
    except FileNotFoundError:
        print(f"Erreur : Le fichier {fichier_config} est introuvable.")
        sys.exit(1)  # Quitte le programme
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier {fichier_config} contient une erreur de format.")
        sys.exit(1)  # Quitte le programme
# Chemin vers le fichier de configuration
CONFIG_FILE = "config.json"
config = charger_configuration(CONFIG_FILE)
# Extraire les valeurs nécessaires du fichier config.json
try:
    ENVOI_INTERVALLE = config["ENVOI_INTERVALLE"]
    ARCHIVE_INTERVALLE = config["ARCHIVE_INTERVALLE"]
    NETTOYAGE_INTERVALLE = config["NETTOYAGE_INTERVALLE"]
except KeyError as e:
    print(f"Erreur : Clé manquante dans le fichier de configuration : {e}")
    sys.exit(1)
# Afficher les valeurs chargées pour confirmation
print(f"ENVOI_INTERVALLE : {ENVOI_INTERVALLE}s")
print(f"ARCHIVE_INTERVALLE : {ARCHIVE_INTERVALLE}s")
print(f"NETTOYAGE_INTERVALLE : {NETTOYAGE_INTERVALLE}s")
# Chemins locaux vers les dossiers "archive" et "backup_archive"
ARCHIVE_DIRECTORY = os.path.join(os.getcwd(), "archive")
BACKUP_DIRECTORY = os.path.join(os.getcwd(), "backup_archive")
# Assurez-vous que les dossiers existent
if not os.path.exists(ARCHIVE_DIRECTORY):
    os.makedirs(ARCHIVE_DIRECTORY)
if not os.path.exists(BACKUP_DIRECTORY):
    os.makedirs(BACKUP_DIRECTORY)
TEMP_ARCHIVE_FILE = "temp_archive.json"  # Fichier temporaire pour archivage
sys.stdout.reconfigure(encoding='utf-8')

################################Générer des données de capteurs####################################################
def generer_donnees():
    date_formatee = datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")
    data = {
        "temperature": 22,
        "humidity": 50,
        "timestamp": date_formatee
    }
    return data

################################Fonction pour stocker les données localement#######################################
def stocker_localement(donnees):
    try:
        with open(LOCAL_STORAGE_FILE, "r") as fichier:
            data = json.load(fichier)  # Lire et charger les données JSON existantes
    except FileNotFoundError:
        data = []  # Si le fichier n'existe pas, on initialise une liste vide
    data.append(donnees)  # Ajouter les nouvelles données à la liste
    with open(LOCAL_STORAGE_FILE, "w") as fichier:
        json.dump(data, fichier, indent=4)  # Réécrit le fichier avec les données mises à jour
        
################################Fonction pour envoyer les données au serveur#######################################
def envoyer_donnees():
    try:
        with open(LOCAL_STORAGE_FILE, "r") as fichier:  # Lis le fichier pour obtenir les données existantes
            data = json.load(fichier)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Aucune donnée à envoyer.")
        return
    # Sauvegarder une copie temporaire pour l'archivage
    with open(TEMP_ARCHIVE_FILE, "w") as temp_file:
        json.dump(data, temp_file, indent=4)
    data_non_envoyee = []
    for entry in data:
        try:
            response = requests.post(SERVER_URL, json=entry)  # Envoi des données au serveur en POST
            if response.status_code == 200:
                print(f"Données envoyées avec succès : {entry}")
            else:
                print(f"Erreur d'envoi : {response.status_code}")
                data_non_envoyee.append(entry)
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            data_non_envoyee.append(entry)
    # Réécriture des données non envoyées
    with open(LOCAL_STORAGE_FILE, "w") as fichier:
        json.dump(data_non_envoyee, fichier, indent=4)
    print(f"{len(data_non_envoyee)} données non envoyées sauvegardées localement.")
    
################################Fonction pour archiver les données###############################################
def archiver_donnees():
    try:
        with open(TEMP_ARCHIVE_FILE, "r") as fichier:
            data = json.load(fichier)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Aucune donnée à archiver.")
        return

    if not data:
        print("Aucune nouvelle donnée à archiver.")
        return
    # Conversion des données en DataFrame
    df = pd.DataFrame(data)
    date_now = datetime.now()
    horodatage = date_now.strftime("%Y-%m-%d_%H-%M")
    heure_archive = date_now.strftime("%Hh%M")
    # Construction des chemins pour Excel et CSV
    fichier_excel = os.path.join(ARCHIVE_DIRECTORY, f"archive_{horodatage}_heure_{heure_archive}.xlsx")
    fichier_csv = os.path.join(ARCHIVE_DIRECTORY, f"archive_{horodatage}_heure_{heure_archive}.csv")
    # Enregistrement en Excel et CSV
    df.to_excel(fichier_excel, index=False, engine='openpyxl')
    df.to_csv(fichier_csv, index=False)
    print(f"Fichiers archivés : {fichier_excel} et {fichier_csv}")
    # Supprimer le fichier temporaire
    open(TEMP_ARCHIVE_FILE, "w").write("[]")
    
################################Fonction pour nettoyer les anciennes archives####################################
def nettoyer_archives():
    os.makedirs(BACKUP_DIRECTORY, exist_ok=True)  # Créer le dossier de sauvegarde s'il n'existe pas
    # Générer un graphique après nettoyage
    generer_graphique()
    for fichier in os.listdir(ARCHIVE_DIRECTORY):
        chemin_fichier = os.path.join(ARCHIVE_DIRECTORY, fichier)
        chemin_sauvegarde = os.path.join(BACKUP_DIRECTORY, fichier)
        if os.path.isfile(chemin_fichier):
            try:
                if fichier.endswith('.csv') or fichier.endswith('.xlsx'):
                    os.rename(chemin_fichier, chemin_sauvegarde)  # Déplacement vers le dossier de sauvegarde
                    print(f"Fichier sauvegardé : {chemin_fichier} -> {chemin_sauvegarde}")
            except PermissionError:
                print(f"Impossible de déplacer (fichier utilisé) : {chemin_fichier}")
                
################################Fonction principale pour collecter, stocker et envoyer périodiquement les données###
def collecter_et_envoyer():
    dernier_envoi = time.time()
    dernier_archive = time.time()
    dernier_nettoyage = time.time()
    while True:
        # Collecte des données
        donnees = generer_donnees()
        print(f"Données collectées : {donnees}")
        # Stockage local
        stocker_localement(donnees)
        # Envoi périodique
        if time.time() - dernier_envoi >= ENVOI_INTERVALLE:
            print("Tentative d'envoi des données stockées...")
            envoyer_donnees()
            dernier_envoi = time.time()
        # Archivage périodique
        if time.time() - dernier_archive >= ARCHIVE_INTERVALLE:
            print("Archivage des données...")
            archiver_donnees()
            dernier_archive = time.time()
        # Nettoyage périodique toutes les 3 minutes
        if time.time() - dernier_nettoyage >= NETTOYAGE_INTERVALLE:  # 180 secondes = 3 minutes
            print("Nettoyage des anciennes archives...")
            nettoyer_archives()
            dernier_nettoyage = time.time()
        # Attente de 5 secondes entre chaque collecte
        time.sleep(5)
        
##########################Création de graphiques pour les données archivées##########################
def generer_graphique():
    # Récupérer tous les fichiers CSV dans le dossier d'archives
    fichiers_csv = [os.path.join(ARCHIVE_DIRECTORY, f) for f in os.listdir(ARCHIVE_DIRECTORY) if f.endswith('.csv')]
    if not fichiers_csv:
        print("Aucun fichier CSV disponible pour générer un graphique.")
        return
    # Lire et concaténer les données de tous les fichiers CSV
    df_list = [pd.read_csv(fichier) for fichier in fichiers_csv]
    df_combined = pd.concat(df_list, ignore_index=True)
    # Générer un graphique
    plt.figure(figsize=(10, 5))
    plt.plot(df_combined['timestamp'], df_combined['temperature'], label='Température')
    plt.plot(df_combined['timestamp'], df_combined['humidity'], label='Humidité')
    plt.xlabel("Horodatage")
    plt.ylabel("Valeurs")
    plt.title("Température et Humidité au cours du temps")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{ARCHIVE_DIRECTORY}graphique_combined.png")
    plt.close()
    print(f"Graphique généré : {ARCHIVE_DIRECTORY}graphique_combined.png")

####################################Démarrage du client########################################################################
if __name__ == "__main__":
    os.makedirs(ARCHIVE_DIRECTORY, exist_ok=True)  # Créer le dossier d'archivage s'il n'existe pas
    print("Démarrage du client...")
    collecter_et_envoyer()
             