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
            [155, 65, 35, 4.5, 157.5, 156, 2250],
            [225, 65, 100, 2, 200, -133, 520],
            [60, 150, 100, 2, 200, -133, 520],
            [140, 155, 15, 4.5, 67.5, 154, 2250]
        ],
        columns=['Start Temp (C)', 'End Temp (C)', 'Flow Rate (kg/s)', 
                 'Heat Capacity (kJ/kg/K)', 'm*Cp (kW/K)', 
                 'Boiling Point (C)', 'Heat of Vaporization (kJ/kg)']
        )
        
        self.approachT = [5, 10, 20]

    @staticmethod
    def HeatDuty(
            m,
            cp, 
            t0,
            t1,
            phaseChange: bool = False,
            heatVap: float = 0 
        ):
        
        kW = (q(m, 'kg/s') * q(cp, 'kJ/kg/degK') * q(t1 - t0, 'degK')).to('kW')
        
        if not phaseChange: return kW
        else: 
            if heatVap == 0: raise Exception("Specifiy heat of vaporization")
            return kW + q(m, 'kg/s') * q(heatVap, 'kJ/degK')
        
    def asd(self):
        print(self.df)
        
        
PinchProj().asd()