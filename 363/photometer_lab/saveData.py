import serial
import pandas as pd
import json

from time import sleep

while True:
    try:
        ser = serial.Serial(port="COM3", baudrate=9600)
        break
    except:
        print("Port not opened")
        sleep(.5)

print("==== Recieving data ====")
df = pd.DataFrame()

try:
    while True:
        data = json.loads(ser.readline().decode())
        df = pd.concat([
                pd.DataFrame({
                            "seconds": [data[0]],
                            "value": [data[1]],
                        }),
                df
            ])

        print(df)
        
except KeyboardInterrupt:
    df.set_index('seconds').to_csv('data.csv')
