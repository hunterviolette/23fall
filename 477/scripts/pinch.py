import pandas as pd 
import pint

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
        
        self.approachT = [0, 5, 10, 15, 20]

    @staticmethod
    def HeatDuty(
            m,
            cp, 
            t0,
            t1,
            boilingPoint,
            heatVap: float = 0 
        ):
        
        kW = (q(m, 'kg/s') * q(cp, 'kJ/kg/degK') * q(t1 - t0, 'degK')).to('kW')

        if t1 < boilingPoint < t0:
            kW += q(m, 'kg/s') * q(heatVap, 'kJ/kg') * -1

        return kW.magnitude

    @staticmethod
    def CommonRange(list1: list, list2: list, verbose: bool = False):
        assert len(list1) == 2 and len(list2) == 2

        min1, max1 = sorted(list1)
        min2, max2 = sorted(list2)

        commonMin = max(min1, min2)
        commonMax = min(max1, max2)

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
        zdf["deltaT"] = zdf["HotStartT"] - zdf["HotEndT"]

        for zi, zx in zdf.iterrows():
            for i, x in self.df.iterrows():
                if x["Stream Type"] == 'Hot': range1 = [zx["HotStartT"], zx["HotEndT"]]
                else: range1 = [zx["ColdStartT"], zx["ColdEndT"]]

                dT = PinchProj.CommonRange(
                                range1, [x["Start Temp (C)"], x["End Temp (C)"]])
                if dT[0] > 0:
                    if x["Stream Type"] == 'Hot': kW = PinchProj.HeatDuty(
                                                            x["Flow Rate (kg/s)"],
                                                            x["Heat Capacity (kJ/kg/K)"],
                                                            dT[1], 
                                                            dT[2],
                                                            x["Boiling Point (C)"],
                                                            heatVap=x["Heat of Vaporization (kJ/kg)"]
                                                        )
                    else:
                        if i == 3: kW = PinchProj.HeatDuty(
                                x["Flow Rate (kg/s)"],
                                x["Heat Capacity (kJ/kg/K)"],
                                dT[2], 
                                dT[1],
                                x["Boiling Point (C)"],
                                heatVap=x["Heat of Vaporization (kJ/kg)"]
                            )
                        else: kW = PinchProj.HeatDuty(
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

        for x in zdf["Degree Approach"].unique():
            zd = zdf.loc[zdf["Degree Approach"] == x].copy()
            zd["Sum of Net Energy (kW)"] = zd["Net Energy (kW)"] + zd["Net Energy (kW)"].shift(1, fill_value = 0)
            zd.loc[(zd["Sum of Net Energy (kW)"] > 0) & (zd["Sum of Net Energy (kW)"].shift(1, fill_value=0) < 0), 'Pinch Point'] = True
            zd["Pinch Point"] = zd["Pinch Point"].fillna(False)
            print(f"=== Stream table for {x} Degree Approach ===", zd, sep='\n')
        
PinchProj().main()