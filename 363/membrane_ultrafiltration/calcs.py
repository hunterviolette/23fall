import pandas as pd
import pint 
import plotly.graph_objects as go
import plotly.io as pio

from scipy.stats import linregress

pio.templates.default = "plotly_dark"

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
q = uReg.Quantity

df = pd.read_csv('data.csv')

def ResidenceTime(flowRate):
    return (q(flowRate, 'grams/min') / q(.11, 'm**2')).to('grams/s/m**2').magnitude

df["flux (gm/m**2/s)"] = df['perm_flow (gm/min)'].apply(ResidenceTime)

fig = go.Figure()
for x in df.species.unique():
  
  d = df.loc[df["species"] == x]
  
  slope, intercept, r_value, p_value, std_err = linregress(d["perm_dp (psi)"], d["flux (gm/m**2/s)"])
  d["linReg"] = slope * d["perm_dp (psi)"] + intercept

  fig.add_trace(go.Scatter(
                          x=d["perm_dp (psi)"], 
                          y=d["flux (gm/m**2/s)"], 
                          mode='markers', 
                          name=x
                        ))
  
  fig.add_trace(go.Scatter(
                        x=d["perm_dp (psi)"], 
                        y=d["linReg"], 
                        mode='lines', 
                        name=f"{x}-linReg"
                      ))

fig.update_layout(
    title='Membrane Ultrafiltration',
    xaxis_title='Change in Pressure (psi)',
    yaxis_title='Flux (gm/m**2/s)',
    legend=dict(title='Legend'),
)

fig.show()