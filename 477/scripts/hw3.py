from scipy.optimize import root
import pint

import pandas as pd
pd.options.display.float_format = '{:.2e}'.format

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"

uReg.define('dollars = [currency] = 1*$')
uReg.define('oBarrel = 1*barrel')
uReg.define('million_dollars = 1e6 * dollars')
q = uReg.Quantity

from sympy import symbols, solve

class ch10eqns:
    
    def DCF(f, # future value
            i, # hurdle rate
            n, # year discounted to 0
        ): return f * (1 + i)**-n # returns present value
    
    def solve_DCF(p, # present value
            f, # future value
            i, # hurdle interest rate,
            n, # years
            solveFor, # solve variable
            verbose : bool = True,
        ):
        sol = solve(f*(1 + i)**(-n) - p, solveFor)
        
        if verbose:
            print(sol)
        
        return sol
    
    def LinTerp(y1 = 0, # end cash flow
                y0 = 0, # starting cash flow
                x1 = 0, # end year
                x0 = 0, # start year
                x = 0, # year
            ):
        
        return y0  + (y1 - y0) * ((x - x0) / (x1 - x0))
        
    def PBP(fci, # fixed capital investment
            acf, # average cash flow
            verbose: bool = True, # print in terminal
        ):
    
        pbp = fci / acf
            
        if verbose:
            print(f" Payback period: {pbp}")
            
        return pbp
    
    
class HW3(ch10eqns):
    
    def OneND():
        land = 2
        fci = 5.7e9
        nSL = 16 # straight line depreciation, years
        taxR = .3 # tax rate
        i = .12
        
        macrs = {
                "1": .1, "2": .18, "3": .144,
                "4": .1152, "5": .0922, "6": .0737,
                "7": .0655, "8": .0655, "9": .0656,
                "10": .0655, "11": .0328
            }

        df = pd.DataFrame()
        for x in range(1,18):
            if x <= 10: d = macrs[str(x)] 
            else: d = 0
            
            df = pd.concat([df,
                            pd.DataFrame({
                                'year':[x+5],
                                'Revenue':[2.185e9],
                                'Expenses':[1.1e9],
                                'D_16_SL':[fci / nSL],
                                'D_10_MACR':[d * fci]
                            })
                        ], axis=0)

        df.reset_index(drop=True, inplace=True)
        
        df["BT NP (SL)"] = (df["Revenue"] - df["Expenses"] - df["D_16_SL"])
        df["BT NP (MACR)"] = (df["Revenue"] - df["Expenses"] - df["D_10_MACR"])
        df.loc[df["year"] == 21, 'BT NP (MACR)'] += 5e8

        df["AT NP (SL)"] = df["BT NP (SL)"] * (1 - taxR)
        df["AT NP (MACR)"] = df["BT NP (MACR)"] * (1 - taxR)
        
        df["AT CF (SL)"] = df["AT NP (SL)"] + df["D_16_SL"]
        df["AT CF (MACR)"] = df["AT NP (MACR)"] + df["D_10_MACR"]
        
        print(df.drop(['BT NP (SL)', 'BT NP (MACR)'], axis=1))
        
        for x in ["Straight line", "MACR"]:
            if x == "Straight line": col = 'AT CF (SL)'
            else: col = 'AT CF (MACR)'
            
            print(
                f'=== {x} non-discount profitability metrics ===',
                f'PBP: {HW3.PBP(fci, df[col].mean(), verbose=False).__round__(2)}',
                f'CCP (billions): {(df[col].sum() / 1e9).__round__(2)}',
                f'CCR: {(df[col].sum() / fci).__round__(2)}',
                f'ROI: {(df[col].mean() / fci).__round__(2)}',
                sep='\n'
            )
            
    def OneD():
        fci = 5.7e9
        nSL = 16 # straight line depreciation, years
        taxR = .3 # tax rate
        i = .12
        
        macrs = {
                "1": .1, "2": .18, "3": .144,
                "4": .1152, "5": .0922, "6": .0737,
                "7": .0655, "8": .0655, "9": .0656,
                "10": .0655, "11": .0328
            }

        df = pd.DataFrame()
        for x in range(1,22):
            if x <= 16 and x>5: d = macrs[str(x-5)] 
            else: d = 0
            
            startup = {1: 1.71, 2: 1.14, 3: 1.14, 
                       4: 1.14, 5:.6}
            
            if x < 6: rev, exp = -startup[x] * 1e9, 0
            else: rev, exp = 2.185e9, 1.1e9
            
            df = pd.concat([df,
                            pd.DataFrame({
                                'year':[x],
                                'Revenue':[rev],
                                'Expenses':[exp],
                                'D_16_SL':[fci / nSL],
                                'D_10_MACR':[d * fci]
                            })
                        ], axis=0)

        df.reset_index(drop=True, inplace=True)
        
        df["BT NP (SL)"] = (df["Revenue"] - df["Expenses"] - df["D_16_SL"])
        df["BT NP (MACR)"] = (df["Revenue"] - df["Expenses"] - df["D_10_MACR"])
        df.loc[df["year"] == 21, 'BT NP (MACR)'] += 5e8

        df["AT NP (SL)"] = df["BT NP (SL)"] * (1 - taxR)
        df["AT NP (MACR)"] = df["BT NP (MACR)"] * (1 - taxR)
        
        df["AT CF (SL)"] = (df["AT NP (SL)"] + df["D_16_SL"]) * (1 + i)**-df["year"]
        df["AT CF (MACR)"] = (df["AT NP (MACR)"] + df["D_10_MACR"]) * (1 + i)**-df["year"]
        
        print(df.drop(['BT NP (SL)', 'BT NP (MACR)'], axis=1))
                
        for x in ["Straight line", "MACR"]:
            if x == "Straight line": col = 'AT CF (SL)'
            else: col = 'AT CF (MACR)'
            
            pcf = df.loc[df["Revenue"] > 0]
            
            print(
                f'=== {x} discounted profitability metrics ===',
                f'DPBP: {HW3.PBP(fci, pcf[col].mean(), verbose=False).__round__(2)}',
                f'NPV (billions): {(df[col].sum() / 1e9).__round__(2)}',
                f'PVR: {(pcf[col].sum() / fci).__round__(2)}',
                f'IRR: {(df[col].mean() / fci).__round__(2)}',
                sep='\n'
            )
            
    def Two():
        priceG = 2.1e4
        fuelG = (6.5e3/30 * 2.5).__round__(2)
        maintG = 368
        
        priceE = 2.76e4 - 4.5e3
        fuelE = ((6.5e3/28)*7*.17).__round__(2)
        maintE = 203
        
        for z in [[.04, 10], [.1, 10], [.04, 15]]:
            print('=====================')
            for x in [[priceG, fuelG, maintG, 'Gas Car'], [priceE, fuelE, maintE, 'Electric Car']]:
                yoc = x[1] + x[2]
                npv = (-x[0] - yoc * (((1 + z[0])**z[1] - 1) / (z[0] * (1 + z[0])**z[1]))).__round__(2)
                cc = (x[0] * (((1 + z[0] )**z[1] - 1) / ((1 + z[0])**z[1] - 1))).__round__(2)
                ecc = (((x[0] * (1 + z[0])**z[1]) / ((1 + z[0])**z[1] - 1)) + yoc / z[0]).__round__(2)
                eaoc = (x[0] * (z[0] * (1 + z[0])**z[1]) / ((1 + z[0])**z[1] - 1) + yoc).__round__(2)
                
                print(f'===== {x[3]}, i={z[0]}, n={z[1]} =====',
                    f"Price of car: {x[0]}, annual fuel cost: {x[1]}, annual maintenance: {x[2]}",
                    f"Net present value: {npv}",
                    f"Capitalized cost: {cc}",
                    f"Equivalent capitalized cost: {ecc}",
                    f"Equivalent annual operating cost: {eaoc}",
                    sep='\n'
                )
                
    def Three():
        pA, pB = 5.5e4, 7.5e4
        acA, acB = 1.62e4, 1.245e4
        
        def eqn(n, pA=pA, pB=pB, i=.1, yocA=acA, yocB=acB):
            return (pA * ((i * (1 + i)**n) / ((1 + i)**n - 1)) + yocA) \
                - (pB * ((i * (1 + i)**n) / ((1 + i)**n - 1)) + yocB)
            
        sol = root(eqn, x0=10)
        print(f"Years: {sol.x[0].__round__(0)}")