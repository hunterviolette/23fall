import pandas as pd

import pint
uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
q = uReg.Quantity


df = pd.DataFrame([
    {'species': 'o2', 'tmax': 2000, 'cp_r': 3.535, 'a': 3.639, 'b': 0.506, 'c': 0, 'd': -0.227, 'hf':0},
    {'species': 'n2', 'tmax': 2000, 'cp_r': 3.502, 'a': 3.28, 'b': 0.593, 'c': 0, 'd': 0.04, 'hf':0},
    {'species': 'co2', 'tmax': 2000, 'cp_r': 4.467, 'a': 5.457, 'b': 1.045, 'c': 0, 'd': -1.157, 'hf':-393.509},
    #{'species': 'h2o_l', 'tmax': 2000, 'cp_r': 3.502, 'a': 3.28, 'b': 0.593, 'c': 0, 'd': 0.04, 'hf:-285.830},
    {'species': 'h2o_v', 'tmax': 2000, 'cp_r': 4.038, 'a': 3.47, 'b': 1.45, 'c': 0, 'd': .121, 'hf':-241.818},
    {'species': 'ch4', 'tmax': 1500, 'cp_r': 4.217, 'a': 1.702, 'b': 9.081, 'c': -2.164, 'd': 0, 'hf':-74.52},
    #{'species': 'wood', 'tmax': 2000, 'cp_r': 3.502, 'a': 3.28, 'b': 0.593, 'c': 0, 'd': 0.04},
])

t, tRef = q(75, 'degF').to('K').magnitude, q(25, 'degF').to('K').magnitude

for i, x in df.iterrows():
    
    molar_h = q(x["hf"], 'kJ/mol') + q(8.314, 'J/mol/K').to('kJ/mol/K') * \
                                        q( x['a'] * (t - tRef) + \
                                           x['b']*10**-3 / 2 * (t**2 - tRef**2) + \
                                           x['c']*10**-6 / 3 * (t**3 - tRef**3) + \
                                           x['d']*10**5 / -1 * (t**-1 - tRef**-1)
                                        , 'K')

    df.loc[df["species"] == x["species"], 'enthalpy (kJ/mol)'] = molar_h.magnitude

print(df)