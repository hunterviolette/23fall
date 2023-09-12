from scipy.optimize import root
import pandas as pd

pd.options.display.float_format = '{:.2e}'.format

class HW2():
    
    @staticmethod
    def One():
        print('==== Problem 1 ====')

        f = (15 + 20 + 22 + 21 + 26 + 26)*10000
                
        def eqn(i, f=f, p=10**6, m=12, n=6):
            return p * (1 + (i / m))**(n * m) - f
            
        sol = root(eqn, x0=0)
        print(f"Interest rate (%): {sol.x[0]*100}")
        
    @staticmethod
    def Two():
        print('==== Problem 2 ====')
        fci = 85*10**6
        sal, sal0 = 7*10**6, 0
        rev, op = 170*10**6, 99*10**6
        taxr = .25
        macrs = {
                "1": .2, "2": .32, "3": .192,
                "4": .1152, "5": .1152, "6": .0576,
                "7": 0, "8": 0, "9": 0,
                "10": 0, "11": 0
            }

        print("=== Key ===",
            "DEP = Depreciation", 
            "CF = Cash Flow", 
            "NPAT = Net Profit After Tax",
            sep='\n')

        df = pd.DataFrame()
        for x in range(1, 10+1):
            df = pd.concat([
                df,
                pd.DataFrame({
                    "Year": [x],
                    "DEP(sl, sal==0)": [fci / 11],
                    "DEP(sl, sal>0)": [(fci - sal) / 11],
                    "DEP(ma)": [fci * macrs[str(x)]],
                    "CF(sl, sal==0)": [rev - op + fci / 11],
                    "CF(sl, sal>0)": [rev - op + (fci - sal) / 11],
                    "CF(ma)": [rev - op + fci * macrs[str(x)]],
                    "NPAT(sl, sal==0)": [(rev - op + fci / 11)*(1-taxr)],
                    "NPAT(sl, sal>0)": [(rev - op + (fci - sal) / 11)*(1-taxr)],
                    "NPAT(ma)": [(rev - op + fci * macrs[str(x)])*(1-taxr)],
                })
            ])
        
        print(
            '=== Depreciation table ===',
            df, 
            "=== Sum of table ===", 
            df.drop('Year', axis=1).sum(),
            sep='\n'
        )

    @staticmethod
    def Three():
        print('==== Problem 3 ====')
        
        m2, m1, i = 12, 365, .05 
        i2 = m2 * ((1 + i / m1)**(m1 / m2) - 1)
        
        def eqn(a, p=40000, i=i2, m=12, n=5):
            return p * (i / m * (1 + i / m)**(n*m)) / ((1 + i / m)**(n*m) - 1) - a
            
        sol = root(eqn, x0=500)
        print(f"Monthly Payment: {sol.x[0]}")
        

    @staticmethod
    def Four():
        print('==== Problem 4 ====')
        yrs, apr = 15, .0385 
        
        def eqn(a, p=40000, i=apr, m=12, n=5):
            return p * (i / m * (1 + i / m)**(n*m)) / \
                ((1 + i / m)**(n*m) - 1) - a
            
        a = root(eqn, x0=0).x[0]

        def factorial(n):
            if n == 0:
                return 1
            else:
                return n + factorial(n - 1)

        annualMaint = (80 + 65 * factorial(yrs)) / yrs

        print(
            f"Monthly payment: {a}",
            f"Annual Maintenance: {annualMaint}",
            f"Annual Cost: {a*12+annualMaint}",
            sep='\n')
    
    @staticmethod
    def Five():
        print('==== Problem 5 ====')
        
        c2012, c2022 = 585, 816
        x = (c2022 / c2012)**(1/20) - 1
        print(f"Avg Inflation rate (%): {x*100}")
        
    
    @staticmethod
    def All():
        HW2.One()
        HW2.Two()
        HW2.Three()
        HW2.Four()
        HW2.Five()
    
        
HW2.All()