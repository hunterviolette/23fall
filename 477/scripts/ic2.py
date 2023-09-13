from scipy.optimize import root
import pandas as pd

m2, m1, i = 12, 365, .035 
i2 = m2 * ((1 + i / m1)**(m1 / m2) - 1)

p = 27000
def eqn(a, p=p, i=i2, m=m2, n=5):
    return p * (i / m * (1 + i / m)**(n*m)) / ((1 + i / m)**(n*m) - 1) - a

sol = root(eqn, x0=500)

print(
    f"Daily interest: {i2}",
    f"Monthly Payment: {sol.x[0]}",
    f"Interest paid: {sol.x[0]*12*5 - p}",

    sep='\n')

print('==== New Problem ====')
def eqn(f, n=70, c0=74, c1=596.2, y0=1950, y1=2020):
    return (1 + f)**(y1 - y0) * c0 - c1

sol = root(eqn, x0=1)

print(f"Avg Inflation rate (%): {sol.x[0]*100}")

print('==== New Problem ====')
fci = 1.02*10**6
sal, taxr = 20000, .30
rev, op = 35*10**6, 11*10**6

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

yrs = 10
df = pd.DataFrame()
for x in range(1, 10+1):
    df = pd.concat([
        df,
        pd.DataFrame({
            "Year": [x],
            "DEP(sl, sal==0)": [fci / yrs],
            "DEP(sl, sal>0)": [(fci - sal) / yrs],
            "DEP(ma)": [fci * macrs[str(x)]],
            "CF(sl, sal==0)": [rev - op + fci / yrs],
            "CF(sl, sal>0)": [rev - op + (fci - sal) / yrs],
            "CF(ma)": [rev - op + fci * macrs[str(x)]],
            "NPAT(sl, sal==0)": [(rev - op + fci / yrs)*(1-taxr)],
            "NPAT(sl, sal>0)": [(rev - op + (fci - sal) / yrs)*(1-taxr)],
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