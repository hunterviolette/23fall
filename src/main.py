import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


from dash import Dash, html, dash_table, dcc, callback, Input, Output, State
from scipy.interpolate import interp1d
from scipy.stats import linregress
from typing import List

import plotly.io as pio
pio.templates.default = "plotly_dark"

class PLAB:

  @staticmethod
  def ScrapeData(path: str = '3h2') -> pd.DataFrame:
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
  def initConc() -> dict:
    return {
          "a": 10, "b": 5, "c": 2.5, "d": 1.25,
          "e": .625, "f": .312, "g": .155, "h": .075
        }

  @staticmethod
  def ReadData(directory: str) -> pd.DataFrame:
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
      df["voltage"] = df["value"]/1024*5
      df = df.groupby('group', as_index=False).agg({"voltage": ['mean', 'max', 'min']})
      
      df.columns = [f'{col[0]}_{col[1]}' if col[1] != '' else col[0] for col in df.columns]
      
      df.rename({'voltage_mean': 'voltage'}, axis=1, inplace=True)

      df["concentration (mM)"] = df["group"].map(PLAB.initConc())
      return df.round(4)
    
    elif directory == 'rxn_data':
      df["value"] = df["value"] / 1024 * 5
      return df.rename({'value': 'voltage'}, axis=1)

    else:
      print('Directory not found')

  @staticmethod
  def V_to_C(df: pd.DataFrame, voltage: float) -> pd.DataFrame:

    interp = interp1d(df['voltage'], 
                      df['concentration (mM)'],
                      kind='linear', 
                      fill_value='extrapolate'
                    )
    
    return interp(voltage)

  @staticmethod
  def InterpData() -> pd.DataFrame:
    df = PLAB.ReadData('rxn_data')
    df["interp c"] = PLAB.V_to_C(
                        PLAB.ReadData('calib_data'), 
                        df["voltage"]
                      )
    return df.reset_index(drop=True)

  @staticmethod
  def RxnRates() -> pd.DataFrame:
    df, ndf = PLAB.InterpData(), pd.DataFrame()
    for x in df.trial.unique():
      d = df.loc[(df.seconds <= 240) & (df.trial == x)]
      ndf = pd.concat([
        ndf, 
        pd.DataFrame({
          "trial": [x],
          "start time": [d.iloc[-1].at['seconds']],
          "end time": [d.iloc[0].at['seconds']],
          "start conc": [d.iloc[-1].at['interp c']],
          "end conc": [d.iloc[0].at['interp c']],
          "calib conc": [PLAB.initConc()[x[1]]]
        })
      ], axis=0)
    
    ndf["RxnRate (mM/s)"] = (ndf["end conc"] - ndf["start conc"]) / \
                            (ndf["end time"] - ndf["start time"])
    
    ndf["RxnRate (nmol/min)"] = ndf['RxnRate (mM/s)']*3*60
    return ndf[["trial", "calib conc", "RxnRate (nmol/min)", 
                "end conc", "end time", "start conc", "start time",
              ]]

  @staticmethod
  def WebApp(debugState: bool = False) -> None:
    calib = PLAB.ReadData('calib_data')

    app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
    app.layout = html.Div([

        dbc.Row([
          dbc.Col([
            dbc.Row([
              html.H4("Trial Selection (multi-select)"),
              dcc.Dropdown(options=list(PLAB.ReadData('rxn_data').trial.unique()),
                          id='trial_dd', 
                          multi=True, 
                          searchable=True, 
                          clearable=True,
                          placeholder='All'
                        ),
            ]),

            dbc.Row([
              html.H4("Handle Outliers"),
              dcc.Dropdown(options=['Just Outliers', 'Remove Outliers'],
                          placeholder = 'All trials',
                          id='outlier_dd', 
                          multi=False, 
                        ),
            ]),

          ], width=2),

          dbc.Col([
            html.H4("Calibration Table"),
            dash_table.DataTable(
                data = calib.to_dict('records'), 
                columns = [{"name": i, "id": i} for i in calib.columns],
                export_format="csv",
                sort_action='native', 
                page_size=10,
                filter_action='native',
                style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                style_data={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'},
                style_table={'overflowX': 'auto'},
                style_cell={
                    'height': 'auto',
                    'whiteSpace': 'normal'
                }
              )], width=4),

          dbc.Col([
            html.H4("Calibration Plot"),
            dcc.Graph(figure=(go.Figure()
                      .add_trace(go.Scatter(
                          x=calib["group"],
                          y=calib["voltage"],
                          mode='lines+markers', 
                          name='average voltage'
                        ))
                      .add_trace(go.Scatter(
                          x=calib["group"],
                          y=calib["voltage_max"],
                          mode='markers', 
                          name='max value'
                        ))
                      .add_trace(go.Scatter(
                          x=calib["group"],
                          y=calib["voltage_min"],
                          mode='markers', 
                          name='min value'
                          ))
                      ).update_layout(height=335)
                    )
            
            ], width=6),

          ], justify="between"),

        html.Div(id='mfig'),

    ], style={"padding": "10px"}) ## End of html.Div

    @app.callback(
      [
        Output("mfig", 'children')
      ],
      [
        Input('trial_dd', 'value'), Input('outlier_dd', 'value')
      ]
    )
    def update(trials: List[str], outliers: str):
      df, mfig = PLAB.InterpData().rename({"calib c": "[S]"}, axis=1), []
      df, rrdf = df.loc[(df.seconds <= 240)], PLAB.RxnRates().rename({"calib conc": "[S]"}, axis=1) 

      outL = ["3g", "3h", "3h2"]
      if outliers == 'Just Outliers':
        df = df.loc[df["trial"].isin(outL)]
        rrdf = rrdf.loc[rrdf["trial"].isin(outL)]

      elif outliers == 'Remove Outliers':
        df = df.loc[~df["trial"].isin(outL)]
        rrdf = rrdf.loc[~rrdf["trial"].isin(outL)]

      if trials not in [None, []]:
        df = df.loc[df["trial"].isin(trials)]
        rrdf = rrdf.loc[rrdf["trial"].isin(trials)]
      
      slope, intercept, r_value, p_value, std_err = linregress(rrdf['[S]'], rrdf['RxnRate (nmol/min)'])
      rrdf["[S] / v"] = 1 / .392 * rrdf["[S]"] + .3

      mfig.append(
        
          dbc.Row([

            dbc.Col([
              html.H3(f"Substrate concentration [S] per time (All trials)", 
                        className="bg-opacity-50 p-1 m-1 bg-info text-dark fw-bold rounded text-center"),

              dcc.Graph(figure=px.line(
                                df.rename({"interp c": "interpolated concentration (mM)"}, axis=1), 
                                x='seconds', 
                                y='interpolated concentration (mM)',
                                color='trial'
                              ).update_layout(height=450)
                            )
            ], width=7),
            
            dbc.Col([
              html.H3(f"Reaction Rate Table", 
                      className="bg-opacity-50 p-1 m-1 bg-info text-dark fw-bold rounded text-center"),
              
              dash_table.DataTable(
                data = rrdf.round(4).to_dict('records'), 
                columns = [{"name": i, "id": i} for i in rrdf.columns],
                export_format="csv",
                sort_action='native', 
                page_size=12,
                filter_action='native',
                style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                style_data={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'},
                style_table={'overflowX': 'auto', 'whiteSpace': 'normal'},
              )
            ], width=5)

          ], justify="between"),

        )

      mfig.append(
        
          dbc.Row([

            dbc.Col([
              html.H3(f"Michaelis-Menten Plot", 
                      className="bg-opacity-50 p-1 m-1 bg-info text-dark fw-bold rounded text-center"),
              html.H6(f"Linear Trend Fit: r={round(r_value,2)}, p={round(p_value,2)}, std_err={round(std_err,2)}"),

              dcc.Graph(figure=px.line(
                                rrdf, 
                                x='[S]', 
                                y='RxnRate (nmol/min)',
                              ).add_trace(go.Scatter(
                                            x=rrdf['[S]'],
                                            y=slope * rrdf['[S]'] + intercept,
                                            mode='lines',
                                            name=f'Linear Trend',
                              )).update_layout(height=425)
                            )
            ], width=6),
            
            dbc.Col([
              html.H3(f"Hanes-Woolf Plot", 
                      className="bg-opacity-50 p-1 m-1 bg-info text-dark fw-bold rounded text-center"),
              
              html.H6(f"Vmax = .392, V0 = .3"),
              dcc.Graph(figure=px.line(
                                rrdf, 
                                x='[S]', 
                                y='[S] / v',
                            ))
            ], width=6)

          ], justify="between"),

        )

      for t in df.trial.unique():
        ds = df.loc[(df.trial == t)].round(3)
        mfig.append(html.H3(f"Trial: {t}", 
                            className="bg-opacity-50 p-1 m-1 bg-info text-dark fw-bold rounded text-center"))

        mfig.append(

          dbc.Row([

            dbc.Col([
              html.H5("Concentration (mM) per time plot"),
              dcc.Graph(figure=px.line(
                                        ds.rename({"interp c": "interpolated concentration (mM)"}, axis=1), 
                                        x='seconds', 
                                        y='interpolated concentration (mM)',
                                      )
                                    )
            ], width=7),

            dbc.Col([
              html.H5("Concentration table"),
              dash_table.DataTable(
                data = ds.round(4).to_dict('records'), 
                columns = [{"name": i, "id": i} for i in ds.columns],
                export_format="csv",
                sort_action='native', 
                page_size=10,
                filter_action='native',
                style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                style_data={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'},
                style_table={'overflowX': 'auto', 'whiteSpace': 'normal'},
              )
            ], width=5)

          ], justify="between"),
        )
        
        rxnRate = round((ds.iloc[0].at['interp c'] - ds.iloc[-1].at['interp c']) / 
                        (ds.iloc[0].at['seconds'] - ds.iloc[-1].at['seconds']), 6)
        
        mfig.append(html.Div([
                      "==============",
                      html.Br(),
                      "Reaction Rate Equation: ",
                      "where c = concentration, s = seconds",
                      html.Br(),
                      f"Reaction rate, k (mM / s) = (c_at_tMax - c_at_tMin) / (sMax - sMin)",
                      html.Br(),
                      f"k = ({ds.iloc[0].at['interp c']} - {ds.iloc[-1].at['interp c']}) / "
                      f"({ds.iloc[0].at['seconds']} - {ds.iloc[-1].at['seconds']}) = " 
                      f"{rxnRate} (mM / s)",
                      html.Br(),
                      "==============",

                    ])    
                  )

      return [mfig]
            

    app.run(host='0.0.0.0', port=8050, debug=debugState)