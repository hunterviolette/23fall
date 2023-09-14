import pandas as pd
from scipy.interpolate import interp1d

class PLAB:

  @staticmethod
  def ScrapeData(path: str = '3h2'):
    import serial
    import json

    from time import sleep

    while True:
      try:
        ser = serial.Serial(port="COM10", baudrate=9600)
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
        df.set_index('seconds').to_csv(f'{path}.csv')

  @staticmethod
  def ReadData(directory: str):
    import os

    df = pd.DataFrame()
    for file in os.listdir(directory):

      if directory == 'calib_data':
        reader = pd.read_csv(f"{directory}/{file}")
        reader["group"] = file[1]

      elif directory == 'rxn_data':
        reader = pd.read_csv(f"{directory}/{file}")
        reader["trial"] = file.split(".")[0]

      df = pd.concat([df, reader], axis=0)

    if directory == 'calib_data':

      df = (df.groupby('group', as_index=False).mean()
            .drop('seconds', axis=1)
            .rename({'value': 'voltage'}, axis=1)
          )
      
      conc = {
          "a": 10, "b": 5, "c": 2.5, "d": 1.25,
          "e": .625, "f": .312, "g": .155, "h": .075
        }
      
      df["concentration (mM)"] = df["group"].map(conc)
      
      print(df)
      return df
    
    elif directory == 'rxn_data':
      print(df)
      return df

    else:
      print('Directory not found')

  @staticmethod
  def V_to_C(df: pd.DataFrame, voltage: float):

    interp = interp1d(df['voltage'], 
                      df['concentration (mM)'],
                      kind='linear', 
                      fill_value='extrapolate'
                    )
    
    return interp(voltage)

x = PLAB
rxn = x.ReadData('rxn_data')
rxn["interp c"] = x.V_to_C(x.ReadData('calib_data'), rxn["value"])
rxn.to_csv('t.csv')

