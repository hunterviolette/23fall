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
    
    def One():
        bpd = q(1.50e5, 'oBarrel / day')
        land = 2
        nFci = 5 
        fci = 5.7e9
        nFci = 5
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
        for x in range(1,17):
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
        df.loc[df["year"] == 21, 'Revenue'] += 5e8
        
        df["AT NP (SL)"] = (df["Revenue"] - df["Expenses"] - df["D_16_SL"]) * (1 - taxR)
        df["AT NP (MACR)"] = (df["Revenue"] - df["Expenses"] - df["D_10_MACR"]) * (1 - taxR)
        
        df["AT CF (SL)"] = df["AT NP (SL)"] + df["D_16_SL"]
        df["AT CF (MACR)"] = df["AT NP (MACR)"] + df["D_10_MACR"]
        
        print(df)
        
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
                