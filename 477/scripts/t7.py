import pandas as pd
import pint

from math import log10

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)

uReg.define('dollar = [currency] = dollar')
uReg.define('thousand_dollar = 10**3 * dollar')
uReg.define('million_dollar = 10**6 * dollar')

q = uReg.Quantity

class PlantCalc:
    
    def __init__(self) -> None:
        self.appendixCols = ['k1', 'k2', 'k3', 'c1', 'c2', 'c3', 'b1', 'b2']

        self.streamFactor = .92
        self.molecWeights = {
            "Isopropyl Alcohol": q(60.1, 'g/mol'),
            "Acetone": q(58.08, 'g/mol'),
            "Water": q(18.02, 'g/mol'),
        }
        
    def Streams(self):
        
        ipaCost = q(1.44, 'dollar/kg') * q(2670, 'kg/hr')
        waterCost = q(360, 'kg/hr') * q(14.5 / 1000, 'dollar/kg')
        
        feedCost = (ipaCost + waterCost).to('million_dollar/year').__round__(2)
        
        acetoneRev = q(1860, 'kg/hr') * q(2.9, 'dollar/kg')
        gasRev = q(240, 'kg/hr') * q(.5, 'dollar/kg')
        
        revenue = (acetoneRev + gasRev).to('million_dollar/year').__round__(2)
        
        gross_profit = ((revenue - feedCost) * self.streamFactor).__round__(2)
        
        print('==== Stream Calculations ====',
            f"Feed Cost: {feedCost}",
            f"Revenue: {revenue}",
            f"Gross Profit: {gross_profit}",
            sep='\n')

    def Pumps(self):
        coef = {"k1": 3.3892, "k2":.0536, 'k3':.1538,
                "c1":-.3935, "c2":.3957, "c3":-.00226,
                "b1":.189, "b2":1.35}
        
        # MOC, designP, Utility, Shaft Power, Efficiency, Fm
        pumps = [
            ["CS", 10, 'Electric', .43, .4],
            ["CS", 2.2, 'Electric', 1.58, .5],
            ["SS", 2.2, 'Electric', 1.3, .75],
        ]

        fM = {'CS':1.55, 'SS':2.28}

        bareModuleCost = []
        for pump in pumps:
            
            bareModuleCost.append(
                PlantCalc.Cbm(
                    PlantCalc.Cp(coef, pump[3]), # Cp
                    coef, # coefficients
                    PlantCalc.Fp(coef, pump[3]),
                    fM[pump[0]]
                )
            )

        self.pumpCost = sum(bareModuleCost).__round__(2)

        print('==== Pump Calculations ====',
            [round(x,2) for x in bareModuleCost],
            f"Total cost of pumps: {2 * self.pumpCost}", 
            sep='\n')
        
    def HeatExchangers(self):
        coef = pd.DataFrame([
            [4.8306, -.8509, .3187, .03881, -.11272, .08183, 1.63, 1.66],
            [4.8306, -.8509, .3187, -.00164, -.00627, .0123, 1.63, 1.66],
            [4.4646, -.5277, .3955, .03881, -.11272, .08183, 1.63, 1.66],
        ],
        columns=self.appendixCols,
        index=['FloatingHead', 'FloatingHeadHighP', 'KettleReboiler']
        )
        
        # Area, MOC, DesignP, Spec
        heatExs = [
            [83.2, 'CS', 10, 'FloatingHeadHighP'],
            [77.3, 'CS', 2.2, 'FloatingHead'],
            [9.2, 'CS', 2.2, 'FloatingHead'],
            [28.5, 'SS', 2.2, 'KettleReboiler'],
            [75.0, 'CS', 2.2, 'FloatingHead'],
        ]

        fM = {'CS':1, 'SS':1.81}

        bareModuleCost = []
        for hX in heatExs:
            ser = coef.loc[coef.index == hX[-1]].squeeze()
            if hX[2] < 5: 
                ser["c1"], ser["c2"], ser["c3"] = 0, 0, 0

            if hX[0] < 10: hX[0] = 10
            
            bareModuleCost.append(
                PlantCalc.Cbm(
                    PlantCalc.Cp(ser, hX[0]), # Cp
                    ser, # coefficients
                    PlantCalc.Fp(ser, hX[0]),
                    fM[hX[1]]
                )
            )

        self.heatExCost = sum(bareModuleCost).__round__(2)

        print('==== HeatEx Calculations ====',
            [round(x,2) for x in bareModuleCost],
            f"Total cost of Heat Exchangers: {self.heatExCost}", 
            sep='\n')
    
    def FiredHeater(self):
        coef = {"k1": 7.3488, "k2":-1.1666, 'k3':.2028,
                "c1":.1347, "c2":-.2368, "c3":.1021}

        fBm = 2.13 # Bare module factor
        a_ = 3 # Attribute for fired heaters, design P, barg

        self.fHeaterCost = (PlantCalc.Cp(coef, a_) * fBm *
                            PlantCalc.Fp(coef, a_)).__round__(2)
        
        print('==== Fired Heater Calculations ====',
            f"Fired Heater cost: {self.fHeaterCost}",
            sep='\n')

    def All(self):
        PlantCalc.Streams(self)
        PlantCalc.Pumps(self)
        PlantCalc.HeatExchangers(self)
        PlantCalc.FiredHeater(self)


    @staticmethod
    def Cp(coef: pd.Series, a_: float):
        return 10**(coef["k1"] + 
                    coef['k2'] * log10(a_) + 
                    coef['k3'] * log10(a_)**2
                )
    
    @staticmethod
    def Fp(coef: pd.Series, a_: float):
        return 10**(coef['c1'] +
                    coef['c2'] * log10(a_) +
                    coef["c3"] * log10(a_)**2
                )
    
    @staticmethod
    def Cbm(cp: float, coef: pd.Series, fp: float, fm: float):
        return cp * (coef['b1'] + 
                     coef['b2'] * fp * fm
                )

PlantCalc().All()