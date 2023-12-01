import pandas as pd 
import pint
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "plotly_dark"


uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
q = uReg.Quantity

class PinchProj:

    def __init__(self) -> None:
        self.irr = .1
        self.n = 10
        self.sf = .98
        self.U = q(750, 'W/m**2/degK')
        
        self.df = pd.DataFrame([
            [155, 65, 35, 4.5, 157.5, 156, 2250, 'Hot'],
            [225, 65, 100, 2, 200, -133, 520, 'Hot'],
            [60, 150, 100, 2, 200, -133, 520, 'Cold'],
            [140, 155, 15, 4.5, 67.5, 154, 2250, 'Cold']
        ],
        columns=['Start Temp (C)', 'End Temp (C)', 'Flow Rate (kg/s)', 
                'Heat Capacity (kJ/kg/K)', 'm*Cp (kW/K)', 
                'Boiling Point (C)', 'Heat of Vaporization (kJ/kg)', 'Stream Type']
        )
        
        #self.approachT = [0, 5, 10, 15, 20]
        self.approachT = [x for x in range(2, 25, 1)]

    @staticmethod
    def HeatDuty(
            streamType,
            m,
            cp, 
            t0,
            t1,
            boilingPoint,
            heatVap: float = 0 
        ):

        if streamType == "Hot": ty, tx = t1, t0
        else: ty, tx = t0, t1
        
        kW = (q(m, 'kg/s') * q(cp, 'kJ/kg/degK') * q(tx - ty, 'degK')).to('kW')
        if tx < boilingPoint < ty:
            kW += q(m, 'kg/s') * q(heatVap, 'kJ/kg') * -1

        return kW.magnitude

    @staticmethod
    def CommonRange(list1: list, list2: list, verbose: bool = False):
        assert len(list1) == 2 and len(list2) == 2

        min1, max1 = sorted(list1)
        min2, max2 = sorted(list2)

        commonMin, commonMax = max(min1, min2), min(max1, max2)

        if commonMin <= commonMax: 
            if verbose: print(
                            f"Zone Range: {list1}",
                            f"Stream Range: {list2}",
                            f"Shared Range: {[commonMin, commonMax]}",
                            f"dT: {commonMax - commonMin}" 
                        )
            return [commonMax - commonMin, commonMin, commonMax]
        else: 
            if verbose: print("No common range")
            return [0]

    @staticmethod
    def Df_To_HTML(dfs, name: str = 'mdf'):
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

        with open(f'{name}.html', 'w', encoding='utf-8') as file:
            for df in dfs:
                file.write(f"<h2>{df.index.unique()[0][0]} Degree Approach:</h2>")
                file.write(df.style.set_table_styles(style
                            ).format(precision=2
                            ).to_html())
                file.write("<br>")
    def main(self):

        zdf = pd.DataFrame()
        for approachT in self.approachT:
            t = self.df.loc[self.df["Stream Type"] == 'Hot']
            zoneTemps = pd.concat([t["Start Temp (C)"], t["End Temp (C)"]]).unique().tolist()

            t = self.df.loc[self.df["Stream Type"] == 'Cold']
            zoneTemps.extend([x + approachT for x in pd.concat(
                [t["Start Temp (C)"], t["End Temp (C)"]]).unique().tolist()])
            
            zoneTemps = sorted(list(set(zoneTemps)), reverse=False)
            for i in range(len(zoneTemps) - 1):
                zdf = pd.concat([
                    pd.DataFrame([
                        [approachT, zoneTemps[i], zoneTemps[i+1]]], 
                        columns=['Degree Approach', 'HotStartT', 'HotEndT']
                    ), 
                    zdf
                ]).reset_index(drop=True)
        
        zdf["ColdStartT"] = zdf["HotStartT"] - zdf["Degree Approach"]
        zdf["ColdEndT"] = zdf["HotEndT"] - zdf["Degree Approach"]
        zdf["deltaT"] = zdf["HotEndT"] - zdf["HotStartT"]

        for zi, zx in zdf.iterrows():
            for i, x in self.df.iterrows():
                if x["Stream Type"] == 'Hot': range1 = [zx["HotStartT"], zx["HotEndT"]]
                else: range1 = [zx["ColdStartT"], zx["ColdEndT"]]

                dT = PinchProj.CommonRange(
                                range1, [x["Start Temp (C)"], x["End Temp (C)"]])
                if dT[0] > 0:
                    kW = PinchProj.HeatDuty(
                            x["Stream Type"],
                            x["Flow Rate (kg/s)"],
                            x["Heat Capacity (kJ/kg/K)"],
                            dT[2], 
                            dT[1],
                            x["Boiling Point (C)"],
                            heatVap=x["Heat of Vaporization (kJ/kg)"]
                        )
                
                else: kW = 0

                zdf.loc[zdf.index == zi, f'Stream {i+1} Energy (kW)'] = kW

        zdf["Net Energy (kW)"] = zdf[[f"Stream {x} Energy (kW)" for x in range(1,5)]
                                    ].sum(axis=1)

        mdf, udf = [], pd.DataFrame()
        for x in zdf["Degree Approach"].unique():
            zd = zdf.loc[zdf["Degree Approach"] == x].copy()
            zd["Sum of Net Energy (kW)"] = zd["Net Energy (kW)"] + zd["Net Energy (kW)"].shift(1, fill_value = 0)
            zd.loc[(zd["Sum of Net Energy (kW)"] > 0) & (zd["Sum of Net Energy (kW)"].shift(1, fill_value=0) < 0), 'Pinch Point'] = True
            zd["Pinch Point"] = zd["Pinch Point"].fillna(False)

            mdf.append(zd.set_index(['Degree Approach', 'HotStartT', 
                                    'HotEndT', 'ColdStartT', 'ColdEndT']
                                    ).round(2))
            
            if zd['Pinch Point'].value_counts()[True] == 1:

                udf = pd.concat([
                    pd.DataFrame({
                        "Degree Approach": [x],
                        "Heating Utility": [zd.at[zd.loc[zd["Pinch Point"] == True].index.values[0] - 1,
                                                  "Sum of Net Energy (kW)"]],
                        "Cooling Utility": [zd["Sum of Net Energy (kW)"].iloc[-1]]
                    }),
                    udf
                ])
            else:
                udf = pd.concat([
                    pd.DataFrame({
                        "Degree Approach": [x],
                        "Heating Utility": [0],
                        "Cooling Utility": [0]
                    }),
                    udf
                ])
                
        PinchProj.Df_To_HTML(mdf)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
                        x=udf["Degree Approach"],
                        y=udf["Heating Utility"],
                        mode='lines',
                        name='Heating Utility'
                    ))
        
        fig.add_trace(go.Scatter(
                        x=udf["Degree Approach"],
                        y=udf["Cooling Utility"],
                        mode='lines',
                        name='Cooling Utility'
                    ))
                        
        fig.update_layout(
            title='Degree Approach vs Utility Usage',
            xaxis_title='Degree Approach',
            yaxis_title='Utility Usage',
            legend=dict(title='Legend'),
        )
        
        fig.show()

PinchProj().main()