import sympy as sp
import pandas as pd

v_, rho, t = sp.symbols('v_ rho t')
f = v_ * rho / t

v_value = 5.0
rho_value = 2.0
t_value = 1.0

unc_v = v_value * .01
unc_rho = rho_value * .01
unc_t = t_value * .01

sub = {v_: v_value, rho: rho_value, t: t_value}

df = pd.DataFrame()
for comp in [[v_, unc_v], [rho, unc_rho], [t, unc_t]]:
    assert len(comp) == 2
    
    df = pd.concat([
        df,
        pd.DataFrame({
            'Component': [comp[0]],
            'Uncert Value': [comp[1]],
            'Component Uncert': [(sp.diff(f, comp[0]).subs(sub)**2 * comp[1]**2)**.5],
        })
    ])

df = df.astype({"Component Uncert": 'float'})

df["Total Uncert"] = df["Component Uncert"].sum()
df['Relative Uncert'] = df["Component Uncert"] / df["Total Uncert"]

print(df.round(2))