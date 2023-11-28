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

def FluxCalc(flowRate):
    return (q(flowRate, 'grams/min') / q(.11, 'm**2')).to('grams/s/m**2').magnitude

df["flux (gm/m**2/s)"] = df['perm_flow (gm/min)'].apply(FluxCalc)

fig = go.Figure()
for x in df.species.unique():
  
  d = df.loc[df["species"] == x].copy()

  slope, intercept, r_value, p_value, std_err = linregress(d["dp (psi)"], d["flux (gm/m**2/s)"])
  d["linReg"] = slope * d["dp (psi)"] + intercept

  print(d.round(3))

  fig.add_trace(go.Scatter(
                          x=d["dp (psi)"], 
                          y=d["flux (gm/m**2/s)"], 
                          mode='markers', 
                          name=x,
                        ))
  
  fig.add_trace(go.Scatter(
                        x=d["dp (psi)"], 
                        y=d["linReg"], 
                        mode='lines', 
                        name=f"{x}-linReg"
                      ))

text_annotations = [dict(
      x=x,
      y=y + 0.3, 
      text=str(y),
      showarrow=False,
  ) for x, y in zip(df["dp (psi)"], df["flux (gm/m**2/s)"].round(2))]

fig.update_layout(
    title='Membrane Ultrafiltration',
    xaxis_title='Change in Pressure (psi)',
    yaxis_title='Flux (gm/m**2/s)',
    legend=dict(title='Legend'),
    annotations=text_annotations
)

fig.show()