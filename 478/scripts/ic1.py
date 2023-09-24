import pandas as pd

from pathlib import Path

if not Path('data/hc.csv').is_file():
    print('Saving df')
    df = pd.DataFrame()
    for x in range(1,10+1):
        df = pd.concat([df, 
                        pd.DataFrame({
                            'time': [x],
                            'points':[x**2]
                            })
                        ])
    df.to_csv('data/hc.csv', index=False)
else:
    df = pd.read_csv('data/hc.csv')

print(df)


