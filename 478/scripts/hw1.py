from pint import UnitRegistry
from math import pi

uReg = UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
uReg.define('kmol = 10**3 * mol')

q  = uReg.Quantity

tH, tC = 158.93, 141 # in celsius
diamT, lenT = q(1.25, 'inch'), q(8, 'ft') # tube specs
pitch = q(1.5, 'inch') # square pitch

flow = q(1000, 'kmol/h') # molar flow
u_ = q(1140, 'W/(m**2 * delta_degC)') # Heat transfer coefficient 
dH = q(20.8, 'MJ/kmol') # Heat of vaporization

q_ = dH * flow # Heat duty 
dT = q(tH - tC, 'delta_degC') # delta T
area = (q_  / (u_ * dT)).to('ft**2')

saTube = (pi * diamT * lenT).to('ft**2')
numTubes = area / saTube

reboilerA = 3 * numTubes * pitch**2
reboilerD = (2 * (reboilerA / pi)**.5).to('ft')

totalLen = q(8, 'ft') + q(2, 'ft')


print(f"Reboiler Length: {totalLen}",
      f"Reboiler Width: {reboilerD}",
      f"Heat duty: {q_}",
      f"Heat transfer coef: {u_}",
      f"Heat of vaporization: {dH}",
      f"Surface area of tubes: {saTube}",
      f"Number of tubes: {numTubes}",
      sep='\n')