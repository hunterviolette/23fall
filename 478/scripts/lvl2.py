import pandas as pd
import pint

from math import log

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
q = uReg.Quantity

# Design V-701, T-702, E-701, E702, C-701, and P-701 

class Heuristics:
    
    def T_702():
        '''
        Stream 7 -> T-702
            T-702 Bottoms -> Stream 9
            T-702 Tops -> Stream 10 + Stream 11
        '''
        flowF = q(7403.5, 'kmol/h')
        flowB = q(7141.7, 'kmol/h')
        flowD = flowF - flowB 

        def Raoults(T, comp):
            if comp == 'water': a,b,c,d,e = 8.7904, -1433.716, -1.1675, -.007132, 8.164e-6
            else : a,b,c,d,e = 

        alpha = pX / pY
        nMin = log((x / (1-x)) / ((y / (1-y)))) / log(alpha) 

    def HeatX(unit, th1, th2, tc1, tc2, Q, U, F):
        Tlm = ((th1 - tc2) - (th2 - tc1)) / log((th1 - tc2) / (th2 - tc1))
        a = (Q / (U * F * Tlm)).to('m**2')
        
        print(f"=== Calculations for unit {unit} ===",
            f'dTlm: {Tlm}',
            f"Area: {a}", 
            sep='\n'
        )

    def Equipment():
        Heuristics.HeatX( # Table 11.11
            'E-701',
            q(60.2, 'degC'), # th1, stream-3
            q(150, 'degC'), # th2, stream-4
            q(30, 'degC'), # tc1
            q(40, 'degC'), # tc2
            q(61400, 'MJ/h'), # Q, given
            q(1140, 'W/m**2/delta_degC'), # U, gas-to-gas item 8
            .9, # F, item 1
        )
        
        Heuristics.HeatX( # Table 11.11
            'E-702',
            q(224.6, 'degC'), # th1, stream-5
            q(68.5, 'degC'), # th2, stream-6
            q(30, 'degC'), # tc1
            q(40, 'degC'), # tc2
            q(113300, 'MJ/h'), # Q, given
            q(850, 'W/m**2/delta_degC'), # U, gas-to-gas item 8
            .9 # F, item 1
        )

Heuristics.Equipment()