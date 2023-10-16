import pandas as pd
from sympy import symbols
from scipy.optimize import root_scalar

from funcs import CHE477

pd.set_option('display.max_rows', 25)

class HW1(CHE477):

  def One():
    print('==== Problem 1 ====')
    m, p, i = 12, 33835, .039

    for x in [[5, 'A'], [3, 'B'], [1, 'C']]:
      annuity = symbols('x')
      mp = HW1.annuity(
                  p, # Principal 
                  i, # Interest rate
                  m, # Compounding periods
                  x[0], # Years
                  annuity, # annuity 
                  annuity
                ) 
      
      ip = mp*m*x[0] - p # Interest paid

      print(f'== Part {x[1]} ==',
            f'Monthly payment: {mp}', 
            f"Interest paid: {ip}", 
            sep='\n'
          )
    
  def Two():
    print('==== Problem 2 ====')
    aprA = HW1.apyapr(.005, symbols('x'), 1)
    aprB = HW1.apyapr(.045, symbols('x'), 1)

    for x in [[aprA, 'A'], [aprB, 'B']]:
      f = HW1.spca(symbols('x'), # Future 
                  10000, # Principal 
                  x[0], # Interest rate
                  12, # Compounding periods
                  10 # Years
                ) 

      print(f"Part {x[1]}: {x[0]}",
            f"Part c{x[1]}: {round(f,3)}",
          sep='\n')
    
  def Three():
    print("==== Problem 3 ====")
    ford, bank = 33835, 60000
    m, n = 12, 5

    annuity = symbols('x')
    mp = HW1.annuity(
                  ford, # Principal 
                  .039, # Interest rate
                  m, # Compounding periods
                  n, # Years
                  annuity, # annuity 
                  annuity # Solve variable
                ) 

    print(f"Monthly payment {mp}")

    for i in [.005, .045]:
      df = pd.DataFrame()

      for x in range(1, 60+1):
        if x == 1:
          m -= 1
          fnb = bank - mp
          nfnb = bank - ford
        else:
          m = 12
          fnb = df.loc[df["Month"] == x-1].reset_index().at[0,"Balance (fiananced)"] - mp
          nfnb = df.loc[df["Month"] == x-1].reset_index().at[0,"Balance (outright)"]

        df = pd.concat([
              pd.DataFrame({
                "Month": [x],
                "Balance (fiananced)": [HW1.spca(symbols('x'), # Future 
                                              fnb, # Principal 
                                              i, # Interest rate
                                              12, # Compounding periods
                                              1/12 # Years
                                            )],
                "Balance (outright)": [HW1.spca(symbols('x'), # Future 
                                            nfnb, # Principal 
                                            i, # Interest rate
                                            12, # Compounding periods
                                            1/12 # Years
                                          )]
              }), 
              df
            ])
      
      df = df.astype({"Balance (fiananced)": 'float64', "Balance (outright)": 'float64'}).round(2)
      print(f"Interest rate: {i}", df, sep='\n')
  
  def Four():
    print("==== Problem 4 ====")
    n, m = 30 / 12, 12

    def equation(var):
      return 460 * 16.3 - (542 * 4 * (1 + (var / m))**(n*m))
      
    res = root_scalar(equation, bracket=[-2, 2])
    nvdaI = res.root * 100  # Convert to percentage
    
    def equation(var):
      return 35 * 61 - \
            11 * 271 * (1 + (var / m))**(25/12*m) - \
            24 * 124 * (1 + (var / m))**(19/12*m)

    res = root_scalar(equation, bracket=[-2, 2])
    pyplI = res.root * 100  # Convert to percentage

    print(f"NVDA APR: {round(nvdaI,2)}", 
          f"PYPL APR: {round(pyplI,2)}", 
          sep='\n')

  def Five():
    print("==== Problem 5 ====")
    aSalary, bSalary = 85000, 75000
    aMatch, bMatch = .5, 1
    aMax, bMax = .06, .1

    apc, bpc = aSalary * aMax, bSalary * bMax
    act, bct = apc * (1 + aMatch), bpc * (1 + bMatch)

    amc, bmc = act / 12, bct / 12
    i = .07

    df = pd.DataFrame()
    for x in range(1, 120+1):
      if x == 1:
        a, b = amc, bmc

      else:
        a = df.loc[df["x"] == x-1].reset_index().at[0,"A Value"] + amc
        b = df.loc[df["x"] == x-1].reset_index().at[0,"B Value"] + bmc

      df = pd.concat([
            pd.DataFrame({
              "x": [x],
              "A Value": [HW1.spca(symbols('x'), # Future 
                            a, # Principal 
                            i, # Interest rate
                            12, # Compounding periods
                            1/12 # Years
                          )],
              "B Value": [HW1.spca(symbols('x'), # Future 
                            b, # Principal 
                            i, # Interest rate
                            12, # Compounding periods
                            1/12 # Years
                          )]
            }),
            df
          ])
    
    df = df.astype({"A Value": 'float64', "B Value": 'float64'}).round(2)

    print(df,
          "I really tried every angle to find a way to take plan A",
          "Like with higher base salary I can leverage more debt",
          "However your IRA value will also count towards debt-to-equity ratio",
          "So plan B is the move- unless your IRA buys PYPL", sep='\n')

  def All():
    HW1.One()
    HW1.Two()
    HW1.Three()
    HW1.Four()
    HW1.Five()

HW1.All()