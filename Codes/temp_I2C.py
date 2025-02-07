import sys
import board
import busio

def read_temp():

        i2c = busio.I2C(board.SCL,board.SDA)
        print("I2C devices found: ", [hex(i) for i in i2c.scan()])
        result = bytearray(4)

        i2c.writeto(0x28,bytes(0x04))
        i2c.readfrom_into(0x28, result)

        print("resultat octets\n")
        print("0:",result[0]," 1:",result[1], " 2:", result[2], " 3:", result[3])

        humidity = (result[0]<<8) + result[1]
        humidity = (humidity/((2**16)-1))*100

        temperature = (result[2]<<8) + result[3]
        temperature = (temperature/((2**16)-1))*165 - 40

        print("\nhumidity: ", humidity, " temperature: ", temperature)

        return temperature, humidity

