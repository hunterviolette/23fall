import plotly.graph_objects as go
import pandas as pd
import pint 

from scipy.stats import linregress
from math import log

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
q = uReg.Quantity

def RefracCalib():
  x = [0, 0, 0.5, 0.5, 1, 1, 1.5, 1.5, 3, 3, 5, 5]
  y = [1.333, 1.333, 1.3336, 1.3336, 1.3342, 1.3344, 1.335, 1.335, 1.3369, 1.3369, 1.3401, 1.3401]

  df = pd.DataFrame({"Refractometer Reading": x, "Weight Percent PEG (%)": y})

  slope, intercept, r_value, p_value, std_err = linregress(
                                                          df["Refractometer Reading"], 
                                                          df["Weight Percent PEG (%)"])
  df["linReg"] = slope * df["Refractometer Reading"] + intercept

  fig = go.Figure()

  fig.add_trace(go.Scatter(
                          x=df["Refractometer Reading"], 
                          y=df["Weight Percent PEG (%)"], 
                          mode='markers+lines', 
                          name='Calibration Data',
                        ))

  fig.add_trace(go.Scatter(
                          x=df["Refractometer Reading"], 
                          y=df["linReg"], 
                          mode='markers+lines', 
                          name='Linear Fit Calibration Data',
                        ))

  fig.update_layout(title=f"Slope: {slope.__round__(4)}, \
                    Intercept: {intercept.__round__(4)}, \
                    R Value: {r_value.__round__(4)}")

  fig.show()

def PumpCalib():
  x = [300, 400, 500, 600, 700]
  y = [282.975, 383.95, 485.74, 568.26, 661.6]

  df = pd.DataFrame({"Set Flow (mL/min)": x, "Total Flow (mL/min)": y})

  slope, intercept, r_value, p_value, std_err = linregress(
                                                          df["Set Flow (mL/min)"], 
                                                          df["Total Flow (mL/min)"])
  df["linReg"] = slope * df["Set Flow (mL/min)"] + intercept

  fig = go.Figure()

  fig.add_trace(go.Scatter(
                          x=df["Set Flow (mL/min)"], 
                          y=df["Total Flow (mL/min)"], 
                          mode='markers+lines', 
                          name='Calibration Data',
                        ))

  fig.add_trace(go.Scatter(
                          x=df["Set Flow (mL/min)"], 
                          y=df["linReg"], 
                          mode='markers+lines', 
                          name='Linear Fit Calibration Data',
                        ))

  fig.update_layout(title=f"Slope: {slope.__round__(4)}, \
                    Intercept: {intercept.__round__(4)}, \
                    R Value: {r_value.__round__(4)}")

  fig.show()

def TwoPoints():
  df = pd.read_csv('data.csv')
  df = df.loc[df["extraPlots"] == 'x']

  def FluxCalc(flowRate):
      return (q(flowRate, 'grams/min') / q(.11, 'm**2')).to('grams/s/m**2').magnitude
  
  def Flux(flowRate):
      return ((q(flowRate, 'grams/min') / q(.11, 'm**2')).to('grams/s/m**2') / q(1000, 'kg/m**3')).to('m/s').magnitude
  
  def logCalc(conc):
      return log(conc)

  df["flux (gm/m**2/s)"] = df['perm_flow (gm/min)'].apply(FluxCalc)
  df['flux'] = df['perm_flow (gm/min)'].apply(Flux)


  df["ln concentration"] = df["wt% ret"].apply(logCalc)
  df["nW / rho"] = df["flux"]

  fig = go.Figure()
  for x in df.species.unique():
    d = df.loc[df["species"] == x].copy()

    fig.add_trace(go.Scatter(
                            x=d["ln concentration"], 
                            y=d["nW / rho"], 
                            mode='markers', 
                            name=x,
                          ))

  fig.update_layout(
      xaxis_title='ln concentration',
      yaxis_title='Flux / Density (m/s)',
  ).show()

def Table():
  df = pd.read_csv('data.csv')
  df = df.loc[df["species"] == '1.5% peg'].drop(columns=['extraPlots'])

  style = [
      dict(selector="th", props=[("background-color", "#154c79"),
                                  ("color", "white"),
                                  ("border", "1px solid white"),
                                  ("text-align", "center"),
                                  ("font-size", "16px"),
                                  ("padding", "4px"),
                                  ("font-weight", "bold")]),
      dict(selector="td", props=[("background-color", "lightgray"),
                                  ("color", "black"),
                                  ("border", "1px solid black"),
                                  ("text-align", "center"),
                                  ("font-size", "14px"),
                                  ("padding", "4px")]),
  ]

  with open(f'table.html', 'w', encoding='utf-8') as file:
    file.write(df.style.set_table_styles(style
                ).format(precision=2
                ).to_html())

TwoPoints()