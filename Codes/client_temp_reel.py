import time
import requests
import smbus2 as smbus
import temp_I2C  # Librairie pour récupérer la température
import os

# Configuration de l'horloge RTC
RTC_ADDRESS = 0x32  # Adresse I2C du SD2403
bus = smbus.SMBus(1)  # Utilisation du bus I2C 1 sur Raspberry Pi   
    # Conversion entre BCD et décimal
def bcd_to_dec(bcd):
    return ((bcd & 0xF0) >> 4) * 10 + (bcd & 0x0F)

def dec_to_bcd(dec):
    return ((dec // 10) << 4) + (dec % 10)

# Lecture de l'heure depuis l'horloge RTC
def read_rtc():
    data = bus.read_i2c_block_data(RTC_ADDRESS, 0x00, 7)  # Lecture de 7 octets
    return [bcd_to_dec(byte) for byte in data]

# Activation de l'écriture sur l'horloge RTC
def enable_write():
    bus.write_byte_data(RTC_ADDRESS, 0x10, 0x80)
    bus.write_byte_data(RTC_ADDRESS, 0x0F, 0x84)

# Désactivation de l'écriture sur l'horloge RTC
def disable_write():
    bus.write_byte_data(RTC_ADDRESS, 0x0F, 0x00)
    bus.write_byte_data(RTC_ADDRESS, 0x10, 0x00)

# Affichage de l'heure actuelle depuis l'horloge RTC
def display_time():
    date = read_rtc()
    print(f"Sec = {date[0]}   Min = {date[1]}   H = {date[2]}   ", end='')
    print(f"W = {date[3]}   D = {date[4]}   M = {date[5]}   Y = {date[6]}")
    return date

# Configuration du serveur
def send_data():
    server_url = "http://192.168.137.2:5000/upload"
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    while True:
        temperature, humidity = temp_I2C.read_temp()  # Lecture des valeurs du capteur
        date = display_time()  # Récupération de la date actuelle
        timestamp = f"{date[2]}:{date[1]}:{date[0]} {days[date[3]-1]} {date[4]} {months[date[5]-1]} {date[6]}"

        data = {
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "timestamp": timestamp
        }

        try:
            response = requests.post(server_url, json=data)
            if response.status_code == 200:
                print("Données envoyées avec succès", data)
            else:
                print(f"Erreur lors de l'envoi: {response.status_code}")
        except Exception as e:
            print(f"Erreur de connexion: {e}")

        # Sauvegarde des données localement
        with open("data.txt", "a") as f:
            f.write(timestamp + "\n")
            f.write(f"Temperature = {data['temperature']}°C   Humidity = {data['humidity']}%\n\n\n")

        time.sleep(5)  # Attente avant le prochain envoi

if __name__ == "__main__":
    print("Démarrage du client...")
    send_data()
