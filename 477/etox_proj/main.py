import pandas as pd 
import pint
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "plotly_dark"

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"

uReg.define('dollar = [currency] = $')
uReg.define('million_dollars = 1e6 * dollar')
q = uReg.Quantity

class AnotherProject:

  def __init__(self) -> None:
    df = pd.read_csv('data.csv')
    self.streamFactor = .95
    self.coolingGJ = q(0.354, 'dollar/GJ')
    self.heatingGJ = q(17.7, 'dollar/GJ')
    self.etoxRevenue = q(1.687, 'dollar/kg') * q(44.06, 'kg/kmol')
    
    df["etox flow (kmol/h)"] = df["ETOX mole frac"] * df["mole flow (kmol/h)"]
    df = df.drop(columns=['ETOX mole frac', 'mole flow (kmol/h)'])

    def etoxYearly(flowRate):
      return (q(flowRate, 'kmol/h').to('kmol/year') * self.etoxRevenue
                ).to('million_dollars/year').magnitude.__round__(3)

    df["Revenue (million_dollars/yr)"] = df['etox flow (kmol/h)'].apply(etoxYearly)

    def heatingCost(duty):
      return (q(duty, 'GJ/h').to('GJ/year') * self.heatingGJ
                ).to('million_dollars/yr').magnitude.__round__(3)

    def coolingCost(duty):
      return (q(abs(duty), 'GJ/h').to('GJ/year') * self.coolingGJ
                ).to('million_dollars/yr').magnitude.__round__(3)
    
    df["heating cost (million_dollars/yr)"] = df['reboiler duty (GJ/h)'].apply(heatingCost)
    df["cooling cost (million_dollars/yr)"] = df['condenser duty (GJ/h)'].apply(coolingCost)

    df["Profit (million_dollars/yr)"] = df["Revenue (million_dollars/yr)"] - \
                                        df["heating cost (million_dollars/yr)"] - \
                                        df["cooling cost (million_dollars/yr)"]

    self.df = df

  def trayProfit(self):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
                    x=self.df['number of stages'], 
                    y=self.df["Profit (million_dollars/yr)"], 
                    mode='markers', 
                    marker=dict(
                        color=self.df["feed stage"],
                        colorscale='Jet',
                        colorbar=dict(title='Feed Tray')
                    )
                  ))
    
    fig.update_layout(
        xaxis_title='Number of trays',
        yaxis_title='Profit (million dollars/year)',
    ).show()

AnotherProject().trayProfit()