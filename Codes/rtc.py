import smbus2 as smbus
import time
import temp_I2C
import os

RTC_ADDRESS = 0x32  # Adresse I2C du SD2403
bus = smbus.SMBus(1)  # Utilisation du bus I2C 1 sur Raspberry Pi

def bcd_to_dec(bcd):
    return ((bcd & 0xF0) >> 4) * 10 + (bcd & 0x0F)

def dec_to_bcd(dec):
    return ((dec // 10) << 4) + (dec % 10)

def read_rtc():
    data = bus.read_i2c_block_data(RTC_ADDRESS, 0x00, 7)  # Lecture de 7 octets depuis l'adresse 0x00
    return [bcd_to_dec(byte) for byte in data]

def write_rtc():
    enable_write()
    data = [
        0x00,         # Adresse de départ
        dec_to_bcd(00),  # Secondes
        dec_to_bcd(43),   # Minutes
        dec_to_bcd(10),  # Heures (24h)
        dec_to_bcd(2),   # Jour de la semaine (Mercredi)
        dec_to_bcd(4),  # Jour du mois
        dec_to_bcd(2),  # Mois
        dec_to_bcd(25)   # Année (2024)
    ]
    bus.write_i2c_block_data(RTC_ADDRESS, data[0], data[1:])
    disable_write()

def enable_write():
    bus.write_byte_data(RTC_ADDRESS, 0x10, 0x80)  # Activer WRTC1
    bus.write_byte_data(RTC_ADDRESS, 0x0F, 0x84)  # Activer WRTC2 et WRTC3
    
def disable_write():
    bus.write_byte_data(RTC_ADDRESS, 0x0F, 0x00)  # Désactiver WRTC2 et WRTC3
    bus.write_byte_data(RTC_ADDRESS, 0x10, 0x00)  # Désactiver WRTC1

def display_time():
    date = read_rtc()
    print(f"Sec = {date[0]}   Min = {date[1]}   H = {date[2]}   ", end='')
    print(f"W = {date[3]}   D = {date[4]}   M = {date[5]}   Y = {date[6]}")
    return date

if __name__ == "__main__":
    #write_rtc()  # Écriture initiale de l'heure (décommentez si nécessaire)
    days = ["monday","tuesday","wednesday", "thursday", "friday","saturday","sunday"]
    months = ["january","february","march","april","may", "june","july","august","september","october","november","december"]

    while True:
        temperature, humidity = temp_I2C.read_temp()
        date = display_time()
        time.sleep(10)
        f = open("data.txt", "a")
        f.write(str(date[2]) + ":" + str(date[1]) + ":" + str(date[0]))
        f.write(" " + days[date[3]-1] + " " + str(date[4]) + " " + months[date[5]-1] + " " + str(date[6]) + "\n")
        f.write("temperature = "+str(round(temperature,2))+"C°" +"  humidity = " + str(round(humidity,2))+ "%" +"\n\n\n")