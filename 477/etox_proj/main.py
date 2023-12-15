import pandas as pd 
import pint
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "seaborn"

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
    self.ethyCost = (q(332.2, 'kmol/h') * q(28.06, 'kg/kmol') * q(1.49, 'dollar/kg')
                      ).to('million_dollars/year')
    self.comd = q(155.786, 'million_dollars/year')
    
    df["mole flow (kmol/h)"] = 333.2 # Overwrite Aspen Flow
    df["etox flow (kmol/h)"] = df["ETOX mole frac"] * df["mole flow (kmol/h)"]
    df = df.drop(columns=['ETOX mole frac', 'mole flow (kmol/h)'])

    def etoxYearly(flowRate):
      return (q(flowRate, 'kmol/h').to('kmol/year') * self.etoxRevenue
                ).to('million_dollars/year').magnitude.__round__(4)

    df["Revenue (million_dollars/yr)"] = df['etox flow (kmol/h)'].apply(etoxYearly)

    def heatingCost(duty):
      return (q(duty, 'GJ/h').to('GJ/year') * self.heatingGJ
                ).to('million_dollars/yr').magnitude.__round__(4)

    def coolingCost(duty):
      return (q(abs(duty), 'GJ/h').to('GJ/year') * self.coolingGJ
                ).to('million_dollars/yr').magnitude.__round__(4)
    
    df["heating cost (million_dollars/yr)"] = df['reboiler duty (GJ/h)'].apply(heatingCost)
    df["cooling cost (million_dollars/yr)"] = df['condenser duty (GJ/h)'].apply(coolingCost)

    df["Profit (million_dollars/yr)"] = df["Revenue (million_dollars/yr)"] - \
                                        df["heating cost (million_dollars/yr)"] - \
                                        df["cooling cost (million_dollars/yr)"] - \
                                        self.comd.magnitude

    self.df = df

  def trayFigs(self):
    df = self.df.loc[self.df["number of stages"] != 90]
    for x in ["reflux ratio", "feed stage"]:
      fig = go.Figure()
      fig.add_trace(go.Scatter(
                      x=df['number of stages'], 
                      y=df["Profit (million_dollars/yr)"], 
                      mode='markers', 
                      marker=dict(
                          color=df[x],
                          colorscale='Jet',
                          colorbar=dict(title=x)
                        )
                    ))
      
      fig.update_layout(
          title=f'Number of Trays vs. {x.capitalize()} vs. Profit',
          xaxis_title='Number of trays',
          yaxis_title='Profit (million dollars/year)',
      ).show()

  def trayDf(self):
    df, mdf = self.df, pd.DataFrame()

    for x in df["number of stages"].unique():
      d = df.loc[(df["number of stages"] == x)]
      mdf = pd.concat([mdf, 
                      d.loc[(d["Profit (million_dollars/yr)"] == d["Profit (million_dollars/yr)"].max())]
                      ], axis=0)
    
      self.mdf = mdf.drop(columns=[
                          'heating cost (million_dollars/yr)', 
                          "cooling cost (million_dollars/yr)",
                          "Revenue (million_dollars/yr)"
                        ])
    
    md = mdf.loc[mdf["number of stages"] != 90]
    for x in ["reflux ratio", "feed stage"]:
      fig = go.Figure()
      fig.add_trace(go.Scatter(
                      x=md['number of stages'], 
                      y=md["Profit (million_dollars/yr)"], 
                      mode='markers+lines', 
                      marker=dict(
                          color=md[x],
                          colorscale='Jet',
                          colorbar=dict(title=x.capitalize())
                        )
                    ))
      
      annotations = [dict(
        x=x,
        y=y + 1, 
        text=str(y),
        showarrow=False,
          ) for x, y in zip(md["number of stages"], 
                            md["Profit (million_dollars/yr)"].round(3))]
      
      fig.update_layout(
          title=f'Optimal Profit for Number of Trays by {x.capitalize()}',
          xaxis_title='Number of trays',
          yaxis_title='Profit (million dollars/year)',
          annotations=annotations

      ).show()
      
    self.mdf.to_csv('optimal_columns.csv')

x = AnotherProject()
x.trayFigs()
x.trayDf()