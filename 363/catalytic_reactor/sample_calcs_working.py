from math import tanh, pi, log
from scipy.optimize import fsolve

import pandas as pd 
from pint import UnitRegistry

q = UnitRegistry(autoconvert_offset_to_baseunit = True).Quantity

vol = (pi * q(23.4, 'cm') * (q(25, 'mm') / 2)**2).to('mL')
print(vol)

df = pd.DataFrame(
  data=[
    ['coarse', .44, 9.47],
    ['coarse', .179, 11.042],
    ['coarse', .293, 13.319],
    ['fine', .443, 9.474],
    ['fine', .216, 10.83],
    ['fine', .359, 13.173],
  ],
  columns=['column', 'fracConv', 'flowRate (mL/min)'],
  index=['34c', '38c', '48c', '34f', '38f', '48f']
)

def ResidenceTime(flowRate):
    return (vol / q(flowRate, 'mL/min')).to('min').magnitude

df["residenceTime (min)"] = df['flowRate (mL/min)'].apply(ResidenceTime)

def RateConstants(x):
    print(x.name[-1], x.name[0:2])
    return (-log(1 - x["fracConv"]) / q(x["residenceTime (min)"], 'min')
            ).to('1/s').magnitude

df["rateConstant (1/s)"] = df.apply(RateConstants, axis=1)

def Phi(kC, rC, kF, rF):
  def PhiSolve(phi):
      return (
          (1 / tanh(phi) - 1 / phi) / 
          (1 / tanh(phi * rF / rC) - 1 / (phi * rF / rC))
      ) - (kC * rC) / (kF * rF)

  return fsolve(PhiSolve, 1)[0]

print(df)